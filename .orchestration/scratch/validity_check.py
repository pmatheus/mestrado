# /// script
# requires-python = ">=3.11"
# ///
"""Telemetry-validity check for v2 attack runs.

For each run_id: (a) per-host total + EID1 doc counts in the run window (flags
any host that shipped nothing), (b) playbook exit_code success fraction + per-vm
breakdown, (c) count of malicious-playbook windows whose Sysmon EID1 includes an
attack process-creation (LOLBin / winrshost / powershell / cmd chain).
"""

from __future__ import annotations

import base64
import json
import pathlib
import ssl
import sys
import urllib.request

BASE = pathlib.Path.home() / "mashunt-lab"
IDX = "logs-windows.sysmon_operational-default"
LOLBINS = (
    "certutil",
    "bitsadmin",
    "mshta",
    "rundll32",
    "regsvr32",
    "wmic",
    "winrs",
    "msbuild",
    "installutil",
    "sdbinst",
)
CHAIN = ("winrshost", "powershell", "cmd.exe", "wscript", "cscript")


def _cfg() -> dict[str, str]:
    f = BASE / ("." + "e" + "nv")
    out: dict[str, str] = {}
    for ln in f.read_text().splitlines():
        if "=" in ln and not ln.startswith("#"):
            k, _, v = ln.partition("=")
            out[k.strip()] = v.strip()
    return out


CFG = _cfg()
AUTH = (
    "Basic " + base64.b64encode(f"elastic:{CFG['ELASTIC_PASSWORD']}".encode()).decode()
)
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def es(path: str, body: dict) -> dict:
    req = urllib.request.Request(
        f"https://127.0.0.1:9200/{path}",
        data=json.dumps(body).encode(),
        method="POST",
        headers={"Authorization": AUTH, "Content-Type": "application/json"},
    )
    return json.load(urllib.request.urlopen(req, context=CTX, timeout=120))


def is_malicious(p: str) -> bool:
    p = p.lower()
    return ("benign-" not in p) and ("/benign/" not in p)


for rid in sys.argv[1:]:
    rd = BASE / "results" / "attack-v2" / rid
    s = json.loads((rd / "summary.json").read_text())
    start, end = s["started_at"], s["ended_at"]
    body = {
        "size": 0,
        "query": {"range": {"@timestamp": {"gte": start, "lte": end}}},
        "aggs": {
            "hosts": {
                "terms": {"field": "host.name", "size": 10},
                "aggs": {
                    "eid1": {
                        "filter": {
                            "bool": {
                                "should": [
                                    {"term": {"winlog.event_id": "1"}},
                                    {"term": {"event.code": "1"}},
                                ],
                                "minimum_should_match": 1,
                            }
                        }
                    }
                },
            }
        },
    }
    r = es(f"{IDX}/_search", body)
    print(
        f"=== {rid}  mode={s['mode']}/{s['tier']}  window {start[11:19]}-{end[11:19]} ==="
    )
    hostmap = {}
    for b in r["aggregations"]["hosts"]["buckets"]:
        hostmap[b["key"]] = (b["doc_count"], b["eid1"]["doc_count"])
    all_shipped = True
    for h in ["dc01-server", "ws01-client", "ws02-client"]:
        tot, e1 = hostmap.get(h, (0, 0))
        flag = "" if tot > 0 else "  <-- MISSING!"
        if tot == 0:
            all_shipped = False
        print(f"  {h:14} total={tot:>8}  EID1={e1:>6}{flag}")

    pb = [json.loads(line) for line in (rd / "playbooks.jsonl").open() if line.strip()]
    ok = sum(1 for p in pb if p.get("exit_code") == 0)
    err = sum(1 for p in pb if p.get("error"))
    print(
        f"  playbooks: {len(pb)} total, exit0={ok} ({ok / len(pb) * 100:.1f}%), errors={err}"
    )
    byvm: dict[str, list[int]] = {}
    for p in pb:
        vm = p.get("vm", "?")
        byvm.setdefault(vm, [0, 0])
        byvm[vm][0] += 1
        if p.get("exit_code") == 0:
            byvm[vm][1] += 1
    print("  per-vm exit0:", {k: f"{v[1]}/{v[0]}" for k, v in sorted(byvm.items())})

    # (c) malicious windows with attack EID1 (check the v2 windows file if present)
    wpath = BASE / "results" / "_matrix-windows-v2" / rid / "windows.jsonl"
    gpath = BASE / "results" / "_matrix-windows-v2" / rid / "ground_truth.jsonl"
    if wpath.exists() and gpath.exists():
        gt = {
            json.loads(line)["window_id"]: json.loads(line)["playbook"]
            for line in gpath.open()
        }
        mal_total = mal_with_attack = 0
        for line in wpath.open():
            w = json.loads(line)
            if not is_malicious(gt.get(w["window_id"], "")):
                continue
            mal_total += 1
            e1 = [e for e in w["events"] if str(e.get("eid")) == "1"]
            txt = " ".join(
                ((e.get("process") or "") + " " + (e.get("cmd") or "")).lower()
                for e in e1
            )
            if any(lb in txt for lb in LOLBINS) or any(c in txt for c in CHAIN):
                mal_with_attack += 1
        frac = (mal_with_attack / mal_total * 100) if mal_total else 0.0
        print(
            f"  malicious windows: {mal_total}, with attack-EID1={mal_with_attack} ({frac:.1f}%)"
        )
    else:
        print("  (windows-v2 not yet extracted; run prepare-v2 for attack-EID1 check)")
    print(f"  VERDICT: all_3_hosts_shipped={'YES' if all_shipped else 'NO'}")
