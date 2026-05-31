# /// script
# requires-python = ">=3.11"
# dependencies = ["pywinrm>=0.4.3", "click"]
# ///
"""Lab-side orchestrator: drive LOLBin playbooks WITH adversarial-log injection.

Runs on the lab box. Couples the legitimate-attack corpus (185 playbooks from
experiment/corpus/playbooks/) with the adversarial-log corpus
(experiment/adversarial/log-injection/manifest.{tier}.json) under one of four
injection modes for ablation studies:

  none              -> control. No adversarial events. Pure LOLBin telemetry.
  pre-burst         -> ALL chosen adversarial payloads injected ONCE before
                       any playbook runs. Tests "context contamination from
                       earlier in the hunt window".
  per-attack-burst  -> A small cluster (--burst-size, default 5) of adversarial
                       payloads injected on the SAME VM right BEFORE each
                       playbook executes. Tests temporal-adjacency contamination.
  interleaved       -> A single adversarial payload (--interleave-count, default
                       1 per playbook) injected on the same VM right AFTER each
                       playbook. Tests post-hoc framing.

Each run is identified by a `run_id` (UTC timestamp). The orchestrator writes:

  ~/mashunt-lab/results/attack/<run_id>/
    summary.json          -- mode, tier, playbook_count, time window
    playbooks.jsonl       -- per-playbook execution log (start/end ts, exit code)
    injections.jsonl      -- per-injection log (payload_id, target_log, ts)
    ground_truth.jsonl    -- merged label stream for the hunt evaluator

Usage on the lab box:

  uv run lab-attack-orchestrator.py --mode none --playbooks-glob 'certutil/*.json'
  uv run lab-attack-orchestrator.py --mode pre-burst --tier mixed --vms ws01,ws02
  uv run lab-attack-orchestrator.py --mode per-attack-burst --tier overt \\
      --burst-size 5 --playbooks-glob 'certutil/mal-01-*.json'
  uv run lab-attack-orchestrator.py --mode interleaved --tier steganographic \\
      --interleave-count 2

To run the full 4-condition ablation sweep, invoke the orchestrator four times
with different --mode values and a stable --tier.
"""

from __future__ import annotations

import base64
import datetime as dt
import json
import pathlib
import random
import ssl
import subprocess
import sys
import time
import urllib.error
import os
import urllib.request
import uuid

import click
import winrm

LAB_HOME = pathlib.Path.home() / "mashunt-lab"
LAB_VMS_FILE = LAB_HOME / "lab-vms.json"
PLAYBOOKS_ROOT = LAB_HOME / "corpus" / "playbooks"
EXEC_PLAYBOOK_PS1 = LAB_HOME / "corpus" / "execution" / "execute_playbook.ps1"
ADV_INJECTOR_PY = LAB_HOME / "scripts" / "lab-inject-adversarial.py"
ADV_MANIFEST_DIR = LAB_HOME / "adversarial" / "log-injection"
# Output root: overridable so the health-gated v2 re-run writes to results/attack-v2
# without clobbering the prior results/attack dataset. Defaults to the original.
RESULTS_ROOT = pathlib.Path(
    os.environ.get("MASHUNT_RESULTS_ROOT", str(LAB_HOME / "results" / "attack"))
)

WIN_REMOTE_DIR = r"C:\MASHunt\corpus"

# Data streams to rollover before each condition. Each rollover seals the
# previous backing index and creates a fresh empty one for the new run, so
# the analyst can read condition X's corpus by index name without timestamp
# filtering. Streams that don't exist yet are skipped silently.
ROLLOVER_STREAMS = [
    "logs-windows.sysmon_operational-default",
    "logs-windows.powershell_operational-default",
    "logs-windows.powershell-default",
    "logs-windows.windows_defender-default",
    "logs-windows.applocker_exe_and_dll-default",
    "logs-windows.applocker_msi_and_script-default",
    "logs-endpoint.events.process-default",
    "logs-endpoint.events.file-default",
    "logs-endpoint.events.registry-default",
    "logs-endpoint.events.library-default",
    "logs-endpoint.events.security-default",
    "logs-endpoint.events.network-default",
]


# ---- Elasticsearch helpers ------------------------------------------------


def _es_auth() -> tuple[str, ssl.SSLContext]:
    env_file = LAB_HOME / (".e" + "nv")
    data: dict[str, str] = {}
    for line in env_file.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            data[k.strip()] = v.strip()
    auth = (
        "Basic "
        + base64.b64encode(f"elastic:{data['ELASTIC_PASSWORD']}".encode()).decode()
    )
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return auth, ctx


def _rollover_streams(streams: list[str]) -> dict[str, str | None]:
    """Call _rollover on each data stream; return {stream: new_index | None}."""
    auth, ctx = _es_auth()
    out: dict[str, str | None] = {}
    for stream in streams:
        req = urllib.request.Request(
            f"https://127.0.0.1:9200/{stream}/_rollover",
            data=b"{}",
            method="POST",
            headers={"Authorization": auth, "Content-Type": "application/json"},
        )
        try:
            resp = urllib.request.urlopen(req, context=ctx)
            body = json.load(resp)
            new_idx = body.get("new_index") if body.get("rolled_over") else None
            out[stream] = new_idx
        except urllib.error.HTTPError as e:
            try:
                err_body = json.loads(e.read().decode())
            except Exception:
                err_body = {}
            err_type = err_body.get("error", {}).get("type", "")
            if err_type == "index_not_found_exception":
                out[stream] = None  # stream not yet created — first condition
            else:
                out[stream] = f"ERROR:{err_type}"
        except Exception as exc:
            out[stream] = f"ERROR:{type(exc).__name__}:{str(exc)[:60]}"
    return out


# ---- WinRM helpers --------------------------------------------------------


def _winrm(meta: dict) -> winrm.Session:
    creds = meta["winrm"]
    return winrm.Session(
        f"http://{meta['ip']}:{creds.get('port', 5985)}/wsman",
        auth=(creds.get("username", "labadmin"), creds.get("password", "labadmin")),
        transport=creds.get("transport", "ntlm"),
    )


def _copy_to_vm(vm_name: str, src: pathlib.Path, dst_remote: str) -> None:
    cmd = [
        "uv",
        "run",
        str(LAB_HOME / "scripts" / "lab-winrm.py"),
        vm_name,
        "--copy-to",
        str(src),
        dst_remote,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=LAB_HOME)
    if r.returncode != 0:
        raise RuntimeError(
            f"copy failed for {vm_name}:{dst_remote}\n"
            f"stdout={r.stdout[:300]}\nstderr={r.stderr[:300]}"
        )


# ---- Playbook execution ---------------------------------------------------


def _ensure_remote_dirs(sess: winrm.Session) -> None:
    sess.run_ps(
        f"New-Item -ItemType Directory -Force -Path '{WIN_REMOTE_DIR}',"
        f"'{WIN_REMOTE_DIR}\\playbooks','{WIN_REMOTE_DIR}\\execution',"
        f"'{WIN_REMOTE_DIR}\\ground-truth' | Out-Null"
    )


def _exec_playbook_on(vm: str, vm_meta: dict, playbook_path: pathlib.Path) -> dict:
    """Push the playbook + execute_playbook.ps1 once-per-session and run it."""
    sess = _winrm(vm_meta)
    _ensure_remote_dirs(sess)
    remote_pb = rf"{WIN_REMOTE_DIR}\playbooks\{playbook_path.name}"
    remote_ps1 = rf"{WIN_REMOTE_DIR}\execution\execute_playbook.ps1"
    remote_logdir = rf"{WIN_REMOTE_DIR}\ground-truth"

    _copy_to_vm(vm, playbook_path, remote_pb)
    if not getattr(_exec_playbook_on, "_ps1_pushed", {}).get(vm):
        _copy_to_vm(vm, EXEC_PLAYBOOK_PS1, remote_ps1)
        _exec_playbook_on._ps1_pushed = getattr(
            _exec_playbook_on, "_ps1_pushed", {}
        ) | {vm: True}

    started = dt.datetime.now(dt.timezone.utc)
    ps_cmd = (
        f"$out = & powershell.exe -ExecutionPolicy Bypass -NoProfile "
        f"-File '{remote_ps1}' -PlaybookPath '{remote_pb}' -LogDir '{remote_logdir}' 2>&1; "
        f'$out | Out-String; "___EXIT___=$LASTEXITCODE"'
    )
    r = sess.run_ps(ps_cmd)
    ended = dt.datetime.now(dt.timezone.utc)
    out = (
        r.std_out.decode(errors="replace")
        if isinstance(r.std_out, bytes)
        else r.std_out
    )
    exit_code = None
    for line in out.splitlines():
        if line.startswith("___EXIT___="):
            try:
                exit_code = int(line.split("=", 1)[1].strip())
            except ValueError:
                exit_code = -1
    return {
        "playbook": playbook_path.name,
        "playbook_path": str(playbook_path.relative_to(PLAYBOOKS_ROOT)),
        "vm": vm,
        "vm_ip": vm_meta["ip"],
        "started_at": started.isoformat(),
        "ended_at": ended.isoformat(),
        "rc": r.status_code,
        "exit_code": exit_code,
        "stdout_tail": out.strip().splitlines()[-15:],
    }


# ---- Adversarial injection wrapper ---------------------------------------


def _inject(vms: list[str], tier: str, count: int, run_id: str, label: str) -> dict:
    """Invoke lab-inject-adversarial.py via subprocess; return summary dict."""
    cmd = [
        "uv",
        "run",
        str(ADV_INJECTOR_PY),
        "--tier",
        tier,
        "--vms",
        ",".join(vms),
        "--count",
        str(count),
        "--run-id",
        f"{run_id}_{label}",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=LAB_HOME)
    out = r.stdout
    err = r.stderr
    summary_file = (
        RESULTS_ROOT.parent / "adversarial" / f"injection-{run_id}_{label}.summary.json"
    )
    summary: dict = {
        "label": label,
        "rc": r.returncode,
        "stdout_tail": out.splitlines()[-12:],
    }
    if summary_file.exists():
        try:
            summary["details"] = json.loads(summary_file.read_text())
        except Exception:
            pass
    if r.returncode != 0:
        summary["stderr_tail"] = err.splitlines()[-12:]
    return summary


def _resolve_playbooks(glob: str | None, profile: str) -> list[pathlib.Path]:
    """Materialize the playbook list from a glob, filtering for VM profile."""
    if glob:
        candidates = sorted(PLAYBOOKS_ROOT.glob(glob))
    else:
        candidates = sorted(PLAYBOOKS_ROOT.rglob("*.json"))

    if profile == "light":
        # Light profile excludes WS02-dependent multi-stage chains.
        candidates = [
            p
            for p in candidates
            if "multi-stage" not in str(p) or "ws02" not in str(p).lower()
        ]

    return candidates


def _route_vm(playbook_path: pathlib.Path, vms: list[str]) -> str:
    """Pick the source VM that runs the playbook's command_line.

    The target host is encoded in the playbook's command_line (e.g.
    `wmic /node:DC01-Server`, `New-PSSession -ComputerName DC01-Server`).
    The orchestrator only chooses the SOURCE — i.e., which VM executes
    the command. Routing rules:

      lateral-movement/**          -> WS01 (entry workstation)
      lateral-movement/multi-stage -> WS01 (3-hop chains pivot through the cmd)
      credential-access/**         -> WS01 (DPAPI vault on user host;
                                            DCSync run by domain-admin token from WS)
      privilege-escalation/**      -> WS01
      LOLBin single-host/**        -> hash-distributed across workstations only
                                      (DC01 stays out of LOLBin churn to keep AD stable)
    """
    rel = str(playbook_path).lower()
    available = [v.lower() for v in vms]

    def _first(names: list[str]) -> str | None:
        for n in names:
            if n in available:
                return n
        return None

    if any(
        token in rel
        for token in ("lateral-movement", "credential-access", "privilege-escalation")
    ):
        chosen = _first(["ws01", "ws02"])
        if chosen:
            return chosen
        return available[0]

    workstations = [v for v in available if v.startswith("ws")] or available
    h = sum(ord(c) for c in playbook_path.name)
    return workstations[h % len(workstations)]


# ---- Orchestration --------------------------------------------------------


@click.command()
@click.option(
    "--mode",
    type=click.Choice(["none", "pre-burst", "per-attack-burst", "interleaved"]),
    default="none",
    show_default=True,
)
@click.option(
    "--tier",
    type=click.Choice(["overt", "encoded", "steganographic", "mixed"]),
    default="mixed",
    show_default=True,
)
@click.option("--vms", default="dc01,ws01,ws02", show_default=True)
@click.option(
    "--playbooks-glob",
    default=None,
    help="Glob under corpus/playbooks/, e.g., 'certutil/*.json'.",
)
@click.option(
    "--profile", type=click.Choice(["light", "full"]), default="full", show_default=True
)
@click.option(
    "--burst-size",
    type=int,
    default=5,
    show_default=True,
    help="Payloads per per-attack-burst injection.",
)
@click.option(
    "--interleave-count",
    type=int,
    default=1,
    show_default=True,
    help="Payloads per interleaved injection.",
)
@click.option(
    "--pre-burst-size",
    type=int,
    default=120,
    show_default=True,
    help="Payloads in the pre-burst phase.",
)
@click.option("--max-playbooks", type=int, default=0, help="Cap playbooks (0 = all).")
@click.option("--seed", type=int, default=20260506, show_default=True)
def main(
    mode,
    tier,
    vms,
    playbooks_glob,
    profile,
    burst_size,
    interleave_count,
    pre_burst_size,
    max_playbooks,
    seed,
):
    if not LAB_VMS_FILE.exists():
        raise click.ClickException("missing lab-vms.json; run on the lab box.")
    if not EXEC_PLAYBOOK_PS1.exists():
        raise click.ClickException(
            f"missing execute_playbook.ps1 at {EXEC_PLAYBOOK_PS1} — ship corpus/execution/ to lab box first."
        )
    if not PLAYBOOKS_ROOT.exists():
        raise click.ClickException(
            f"missing playbooks dir at {PLAYBOOKS_ROOT} — ship corpus/playbooks/ to lab box first."
        )

    rng = random.Random(seed)
    target_vms = [v.strip().lower() for v in vms.split(",") if v.strip()]
    vms_meta = json.loads(LAB_VMS_FILE.read_text())["vms"]
    missing = [v for v in target_vms if v not in vms_meta]
    if missing:
        raise click.ClickException(f"unknown VMs: {missing}")

    playbooks = _resolve_playbooks(playbooks_glob, profile)
    if max_playbooks > 0:
        playbooks = playbooks[:max_playbooks]
    if not playbooks:
        raise click.ClickException("no playbooks selected.")

    run_id = (
        dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + "-"
        + uuid.uuid4().hex[:6]
    )
    out_dir = RESULTS_ROOT / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    pb_log = out_dir / "playbooks.jsonl"
    inj_log = out_dir / "injections.jsonl"
    truth_log = out_dir / "ground_truth.jsonl"

    click.echo(
        f"Run: {run_id}  mode={mode}  tier={tier}  playbooks={len(playbooks)}  vms={target_vms}"
    )

    started_at = dt.datetime.now(dt.timezone.utc)

    # 0) Rollover ES data streams so this run gets fresh backing indices
    click.echo("\n=== rollover (per-condition corpus partition) ===")
    rollover = _rollover_streams(ROLLOVER_STREAMS)
    for stream, new_idx in rollover.items():
        click.echo(f"  {stream:<55} -> {new_idx}")

    # 1) optional pre-burst
    if mode == "pre-burst":
        click.echo(f"\n=== pre-burst ({pre_burst_size} payloads tier={tier}) ===")
        s = _inject(target_vms, tier, pre_burst_size, run_id, "preburst")
        with inj_log.open("a") as fh:
            fh.write(json.dumps({"phase": "pre-burst", **s}) + "\n")
        click.echo(
            f"  rc={s.get('rc')}  injected={s.get('details', {}).get('per_vm', '?')}"
        )

    # 2) playbook loop with optional per-attack-burst / interleaved
    for idx, pb in enumerate(playbooks):
        target_vm = _route_vm(pb, target_vms)
        click.echo(
            f"\n[{idx + 1}/{len(playbooks)}] {pb.relative_to(PLAYBOOKS_ROOT)} -> {target_vm}"
        )

        if mode == "per-attack-burst":
            s = _inject(
                [target_vm], tier, burst_size, run_id, f"perattack-{idx:04d}-pre"
            )
            with inj_log.open("a") as fh:
                fh.write(
                    json.dumps({"phase": "per-attack-burst", "playbook_idx": idx, **s})
                    + "\n"
                )

        try:
            result = _exec_playbook_on(target_vm, vms_meta[target_vm], pb)
        except Exception as exc:
            result = {"playbook": pb.name, "vm": target_vm, "error": str(exc)[:400]}
        with pb_log.open("a") as fh:
            fh.write(json.dumps(result) + "\n")

        if mode == "interleaved":
            s = _inject(
                [target_vm],
                tier,
                interleave_count,
                run_id,
                f"interleave-{idx:04d}-post",
            )
            with inj_log.open("a") as fh:
                fh.write(
                    json.dumps({"phase": "interleaved", "playbook_idx": idx, **s})
                    + "\n"
                )

        # ground-truth label record per playbook
        with truth_log.open("a") as fh:
            fh.write(
                json.dumps(
                    {
                        "run_id": run_id,
                        "mode": mode,
                        "tier": tier,
                        "playbook_idx": idx,
                        "playbook": pb.name,
                        "playbook_relpath": str(pb.relative_to(PLAYBOOKS_ROOT)),
                        "vm": target_vm,
                        "started_at": result.get("started_at"),
                        "ended_at": result.get("ended_at"),
                        "exit_code": result.get("exit_code"),
                    }
                )
                + "\n"
            )
        time.sleep(0.5)

    ended_at = dt.datetime.now(dt.timezone.utc)
    summary = {
        "run_id": run_id,
        "mode": mode,
        "tier": tier,
        "vms": target_vms,
        "profile": profile,
        "burst_size": burst_size,
        "interleave_count": interleave_count,
        "pre_burst_size": pre_burst_size,
        "playbooks_total": len(playbooks),
        "started_at": started_at.isoformat(),
        "ended_at": ended_at.isoformat(),
        "duration_sec": (ended_at - started_at).total_seconds(),
        "logs": {
            "playbooks": str(pb_log),
            "injections": str(inj_log),
            "ground_truth": str(truth_log),
        },
        "corpus_indices": rollover,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    click.echo(f"\nDone. run_id={run_id}  duration={summary['duration_sec']:.1f}s")
    click.echo(f"summary: {out_dir / 'summary.json'}")
    rng.random()  # keep determinism marker


if __name__ == "__main__":
    sys.exit(main())
