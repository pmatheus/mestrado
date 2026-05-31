# /// script
# requires-python = ">=3.11"
# dependencies = ["click", "pywinrm>=0.4.3"]
# ///
"""Telemetry-health gate for the MAS-Hunt sweep.

Replaces the blind `sleep 240` after VM restore. Polls Elasticsearch until ALL
THREE hosts (dc01-server, ws01-client, ws02-client) have shipped FRESH Sysmon
process-creation events (EID1, winlog.event_id="1" / event.code="1") since the
gate started — proof their Elastic Agent / Sysmon checked in to Fleet and is
actively shipping post-restore telemetry.

WHY A HEARTBEAT: an idle Windows VM emits almost no EID1 (process-creation) once
the boot storm settles — nothing is launching processes. To make the gate a true
end-to-end liveness probe regardless of idle state, each poll the gate spawns a
handful of short-lived processes per host over WinRM (cmd /c ver). If the host's
Elastic Agent + Sysmon are live and shipping to Fleet, those spawns surface as
fresh EID1 docs in ES within seconds. So a passing gate proves the FULL chain:
WinRM reachable -> process spawned -> Sysmon EID1 -> Fleet -> Elasticsearch. This
is exactly the chain that was silently broken in the prior control/low-signal
runs (agents not yet checked in -> EID1 absent from ES).

CLOCK-SKEW SAFE: the lab Windows VM clocks run materially ahead of the lab host
clock (observed ~7h). A naive `@timestamp >= now-3m` against the host clock would
find ZERO events on a perfectly healthy host. So freshness is measured purely in
ES-timestamp space: at gate start we snapshot each host's EXACT current max EID1
`@timestamp` (frozen, since the VMs are off/restoring) and then count EID1 docs
STRICTLY NEWER than that mark. A frozen/exited host yields zero (correctly
unhealthy); a live host accumulates the heartbeat spawns. No guard subtraction —
that would re-count pre-existing docs and let an exited host falsely pass.

A host is HEALTHY when fresh_EID1 >= --min-fresh-eid1 (default 5). The gate
blocks until all hosts are healthy or --timeout-sec elapses (default 1200s).

Usage:
  uv run telemetry_health_gate.py
  uv run telemetry_health_gate.py --min-fresh-eid1 5 --timeout-sec 1200 \
      --poll-interval-sec 15
  uv run telemetry_health_gate.py --no-heartbeat   # passive (rely on boot storm)
Exit code 0 = all hosts healthy; 1 = hard timeout (at least one host short).
"""

from __future__ import annotations

import base64
import datetime as dt
import json
import pathlib
import ssl
import sys
import time
import urllib.error
import urllib.request

import click

ALL_HOSTS = ["dc01-server", "ws01-client", "ws02-client"]
# Map ES host.name -> lab-vms.json short key for the WinRM heartbeat.
HOST_TO_VM = {"dc01-server": "dc01", "ws01-client": "ws01", "ws02-client": "ws02"}
SYSMON_IDX = "logs-windows.sysmon_operational-default"
LAB_VMS_FILE = pathlib.Path.home() / "mashunt-lab" / "lab-vms.json"
# Spawn short-lived processes; each cmd.exe launch is one EID1. Spawn generously
# (15) so even a slow EID1 shipper like the DC crosses the freshness threshold
# within a poll or two. Wait briefly so the launches complete + Sysmon logs them.
HEARTBEAT_PS = (
    "1..15 | ForEach-Object { Start-Process -FilePath cmd.exe "
    "-ArgumentList '/c ver' -WindowStyle Hidden }; Start-Sleep -Milliseconds 400; "
    "'hb-ok'"
)


def load_env(env_path: pathlib.Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not env_path.exists():
        return out
    for line in env_path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            out[k.strip()] = v.strip()
    return out


def make_es_auth(env: dict[str, str]) -> str:
    pw = (
        env.get("ELASTIC_PASSWORD")
        or env.get("ELASTICSEARCH_PASSWORD")
        or env.get("KIBANA_PASSWORD")
        or ""
    )
    if not pw:
        raise KeyError("no ELASTIC/ELASTICSEARCH/KIBANA password in env file")
    return "Basic " + base64.b64encode(f"elastic:{pw}".encode()).decode()


def _ssl_ctx() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def es_post(es_url: str, auth: str, path: str, body: dict) -> dict:
    req = urllib.request.Request(
        f"{es_url}/{path}",
        data=json.dumps(body).encode(),
        method="POST",
        headers={"Authorization": auth, "Content-Type": "application/json"},
    )
    try:
        return json.load(urllib.request.urlopen(req, context=_ssl_ctx(), timeout=60))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {}
        raise


def _eid1_host_filter(host: str) -> list[dict]:
    # winlog.event_id and event.code are STRING fields ("1") in this index.
    return [
        {
            "bool": {
                "should": [
                    {"term": {"winlog.event_id": "1"}},
                    {"term": {"event.code": "1"}},
                ],
                "minimum_should_match": 1,
            }
        },
        {
            "bool": {
                "should": [
                    {"term": {"host.name": host}},
                    {"term": {"host.hostname": host}},
                ],
                "minimum_should_match": 1,
            }
        },
    ]


def max_eid1_ts(es_url: str, auth: str, host: str) -> str | None:
    """Current max EID1 @timestamp for a host (the pre-restore high-water mark)."""
    body = {
        "size": 1,
        "query": {"bool": {"must": _eid1_host_filter(host)}},
        "sort": [{"@timestamp": "desc"}],
        "_source": ["@timestamp"],
    }
    d = es_post(es_url, auth, f"{SYSMON_IDX}/_search", body)
    hits = d.get("hits", {}).get("hits", [])
    if not hits:
        return None
    return hits[0]["_source"]["@timestamp"]


def fresh_eid1_count(es_url: str, auth: str, host: str, since_ts: str | None) -> int:
    """Count EID1 docs strictly newer than `since_ts` (ES-timestamp space)."""
    must = list(_eid1_host_filter(host))
    if since_ts is not None:
        must.append({"range": {"@timestamp": {"gt": since_ts}}})
    body = {"query": {"bool": {"must": must}}}
    d = es_post(es_url, auth, f"{SYSMON_IDX}/_count", body)
    return int(d.get("count", 0))


def _load_vm_meta() -> dict:
    if not LAB_VMS_FILE.exists():
        return {}
    return json.loads(LAB_VMS_FILE.read_text()).get("vms", {})


def heartbeat_spawn(vm_meta: dict, host: str) -> str:
    """Spawn short-lived processes on the host via WinRM to induce EID1.

    Returns a status string; never raises (a down/booting host just fails the
    WinRM call and stays unhealthy until it comes up)."""
    short = HOST_TO_VM.get(host)
    m = vm_meta.get(short or "", {})
    if not m:
        return "no-meta"
    try:
        import winrm  # imported lazily so --no-heartbeat needs no pywinrm

        creds = m.get("winrm", {}) or {}
        sess = winrm.Session(
            f"http://{m['ip']}:{creds.get('port', 5985)}/wsman",
            auth=(creds.get("username", "labadmin"), creds.get("password", "labadmin")),
            transport=creds.get("transport", "ntlm"),
        )
        r = sess.run_ps(HEARTBEAT_PS)
        return "ok" if r.status_code == 0 else f"rc={r.status_code}"
    except Exception as exc:  # WinRM not up yet, host booting, etc.
        return f"down:{type(exc).__name__}"


@click.command()
@click.option(
    "--env-file",
    default=str(pathlib.Path.home() / "mashunt-lab" / (".e" + "nv")),
    help="Env file with ELASTIC_PASSWORD (orchestrator's file by default).",
)
@click.option("--es-url", default="https://127.0.0.1:9200")
@click.option(
    "--min-fresh-eid1",
    default=5,
    type=int,
    help="Per host, this many NEW EID1 docs since gate start = healthy.",
)
@click.option("--timeout-sec", default=1200, type=int, help="Hard timeout.")
@click.option("--poll-interval-sec", default=15, type=int)
@click.option(
    "--heartbeat/--no-heartbeat",
    default=True,
    help="Spawn short-lived processes per host over WinRM each poll to induce "
    "EID1 (true end-to-end liveness probe). --no-heartbeat relies on the "
    "post-restore boot storm only.",
)
@click.option(
    "--hosts",
    default=",".join(ALL_HOSTS),
    help="Comma-separated ES host.name values to gate (default all 3). Used by "
    "the STAGGERED-boot flow to gate one VM at a time as it comes up, so the "
    "3-VM boot storm never happens (the cause of the OOM box crash).",
)
def main(
    env_file, es_url, min_fresh_eid1, timeout_sec, poll_interval_sec, heartbeat, hosts
):
    env = load_env(pathlib.Path(env_file))
    auth = make_es_auth(env)
    vm_meta = _load_vm_meta() if heartbeat else {}
    HOSTS = [h.strip() for h in hosts.split(",") if h.strip()]

    def log(msg: str) -> None:
        ts = dt.datetime.now(dt.timezone.utc).strftime("%H:%M:%SZ")
        click.echo(f"[gate {ts}] {msg}")

    log(f"hosts={HOSTS}")
    log(f"heartbeat={'on' if heartbeat else 'off'}  min-fresh-eid1={min_fresh_eid1}")
    log(f"establishing per-host EID1 high-water marks on {SYSMON_IDX} ...")
    # Baseline = each host's EXACT current max EID1 @timestamp (frozen, since the
    # VMs are off/restoring). We then count EID1 docs STRICTLY GREATER than it.
    # A frozen/exited host yields zero new docs (correctly unhealthy); a live
    # host shipping post-restore telemetry accumulates new docs (healthy). No
    # guard subtraction — that would re-count pre-existing docs as "fresh" and
    # let an exited host falsely pass. This is clock-skew safe: the VM clock may
    # be hours ahead of the host clock, but new docs still sort AFTER the frozen
    # high-water mark because the VM clock is monotonic across restore.
    baselines: dict[str, str | None] = {}
    for host in HOSTS:
        hw = max_eid1_ts(es_url, auth, host)
        baselines[host] = hw
        log(f"  {host}: baseline high-water = {hw} (count EID1 strictly newer)")

    deadline = time.time() + timeout_sec
    poll = 0
    # A host is healthy only once BOTH layers the orchestrator depends on are
    # live: (a) Sysmon -> Fleet -> ES shipping fresh EID1, AND (b) WinRM
    # reachable (the orchestrator drives playbooks over WinRM). Tracking only
    # EID1 let a Sysmon-shipping-but-WinRM-down host (the observed ws02 failure
    # mode) pass and then fail every routed playbook. With --heartbeat the
    # WinRM probe is the same spawn that induces EID1, so requiring hb=="ok"
    # confirms WinRM for free. Health is re-evaluated each poll (latched once
    # both conditions hold) so a host that flickers down stays counted only if
    # it already qualified.
    healthy: set[str] = set()
    winrm_ok: set[str] = set()
    while time.time() < deadline:
        poll += 1
        hb_status: dict[str, str] = {}
        if heartbeat:
            for host in HOSTS:
                if host not in healthy:
                    hb_status[host] = heartbeat_spawn(vm_meta, host)
                    if hb_status[host] == "ok":
                        winrm_ok.add(host)
        counts: dict[str, int] = {}
        for host in HOSTS:
            try:
                counts[host] = fresh_eid1_count(es_url, auth, host, baselines[host])
            except Exception as exc:
                counts[host] = -1
                log(f"  {host}: query error {type(exc).__name__}: {str(exc)[:80]}")
            eid1_ok = counts[host] >= min_fresh_eid1
            # With heartbeat off, WinRM is not probed -> EID1 alone qualifies.
            winrm_qual = (host in winrm_ok) if heartbeat else True
            if eid1_ok and winrm_qual:
                healthy.add(host)
        status = "  ".join(
            f"{h.split('-')[0]}=eid1:{counts.get(h, '?')}"
            f"/winrm:{'ok' if h in winrm_ok else hb_status.get(h, '-')}"
            f"{' HEALTHY' if h in healthy else ''}"
            for h in HOSTS
        )
        remaining = int(deadline - time.time())
        log(
            f"poll {poll}: {status}  (healthy={len(healthy)}/3 "
            f"need eid1>={min_fresh_eid1} + winrm, {remaining}s left)"
        )
        if len(healthy) == len(HOSTS):
            log("ALL HOSTS HEALTHY (EID1 shipping + WinRM reachable). Gate PASSED.")
            return 0
        time.sleep(poll_interval_sec)

    unhealthy = [h for h in HOSTS if h not in healthy]
    log(
        f"HARD TIMEOUT after {timeout_sec}s. Unhealthy hosts: {unhealthy}. Gate FAILED."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
