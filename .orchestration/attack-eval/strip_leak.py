# /// script
# requires-python = ">=3.11"
# ///
"""Build leak-stripped batches from the existing batches/.

The v2 lab telemetry embeds a ground-truth ORACLE: the harness command
`execute_playbook.ps1 -PlaybookPath ...<family>-mal-NN-....json` names the
playbook (hence the label), and base64 `-encodedcommand` blobs carry corpus
seeding. A classifier can read the filename instead of reasoning over behavior,
which confounds any accuracy/ASR comparison. This script removes those events,
keeping the genuine decoded LOLBin process events (rundll32/bitsadmin/etc.) and
the forged-context events (identified by sentinel pids 60001-60005), so the
attack eval tests behavioral reasoning vs forged corroboration on a fair task.

Re-groups into 2 balanced batches per tier (stripped windows are small).
"""

from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "batches"
OUT = ROOT / "batches-stripped"
TIERS = ["A0", "A3"]  # baseline + strong attack
FORGED_PIDS = {60001, 60002, 60003, 60004, 60005}
LEAK_TOKENS = [
    "execute_playbook",
    "playbookpath",
    "mashunt",
    "\\corpus\\",
    "/corpus/",
    "\\adversarial\\",
    "/adversarial/",
    "inject-adversarial",
    "inject_adversarial",
    "-mal-",
    "lat-benign",
    "benign-0",
    "mal-0",
    "-encodedcommand",
]


def is_forged(e: dict) -> bool:
    return e.get("pid") in FORGED_PIDS


def is_leak(e: dict) -> bool:
    blob = ((e.get("cmd") or "") + " " + (e.get("parent_cmd") or "")).lower()
    return any(tok in blob for tok in LEAK_TOKENS)


def main() -> None:
    for tier in TIERS:
        windows = []
        for f in sorted((SRC / tier).glob("*.json")):
            for w in json.load(f.open()):
                kept = [e for e in w["events"] if is_forged(e) or not is_leak(e)]
                w2 = dict(w)
                w2["events"] = kept
                w2["n_events"] = len(kept)
                windows.append(w2)
        # re-split into 3 balanced groups (stripped windows are small)
        windows.sort(key=lambda w: w["window_id"])
        groups = {"H1": windows[0::3], "H2": windows[1::3], "H3": windows[2::3]}
        outdir = OUT / tier
        outdir.mkdir(parents=True, exist_ok=True)
        for g, ws in groups.items():
            (outdir / f"{g}.json").write_text(json.dumps(ws))
        sizes = {g: sum(len(json.dumps(w)) for w in ws) for g, ws in groups.items()}
        desc = " ".join(
            f"{g}={len(ws)}({sizes[g] // 1000}KB)" for g, ws in groups.items()
        )
        print(f"{tier}: {len(windows)} windows -> {desc}")


if __name__ == "__main__":
    main()
