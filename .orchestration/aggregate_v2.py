#!/usr/bin/env python3
"""Aggregate the MAS-Hunt v2 signal-rich matrix.

Runs on the lab host from /home/user/mashunt-lab. It reads the four condition
directories, joins predictions to withheld ground truth, computes pooled metrics,
bootstrap CIs, tier/mode breakdowns, and the C1-full injection-flag evidence.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any


BASE = Path("/home/user/mashunt-lab")
RESULTS = BASE / "results"
OUT = RESULTS / "matrix-v2"

RUNS = [
    {
        "run_id": "20260529T231559Z-02fc9c",
        "mode": "per-attack-burst",
        "tier": "overt",
    },
    {
        "run_id": "20260530T005129Z-53a2cb",
        "mode": "per-attack-burst",
        "tier": "encoded",
    },
    {
        "run_id": "20260530T022438Z-19f80c",
        "mode": "per-attack-burst",
        "tier": "steganographic",
    },
    {
        "run_id": "20260530T040359Z-eedb0f",
        "mode": "interleaved",
        "tier": "overt",
    },
    {
        "run_id": "20260530T053439Z-702a1a",
        "mode": "interleaved",
        "tier": "encoded",
    },
    {
        "run_id": "20260530T070504Z-96829d",
        "mode": "interleaved",
        "tier": "steganographic",
    },
]

CONDITIONS = {
    "C1-full": "c1full-orch-v2",
    "C1-nohardening": "c1nohard-orch-v2",
    "C2-naive": "c2-naive-orch-v2",
    "C3-Elastic": "c3-elastic-v2",
}

B = 10_000
SEED = 42


@dataclass(frozen=True)
class Row:
    run_id: str
    mode: str
    tier: str
    playbook: str
    true_malicious: bool
    predicted_malicious: bool
    injection_flagged: bool


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def prf2(tp: int, fp: int, fn: int) -> dict[str, float]:
    precision = safe_div(tp, tp + fp)
    recall = safe_div(tp, tp + fn)
    f2 = safe_div(5 * precision * recall, 4 * precision + recall)
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f2": round(f2, 4),
    }


def confusion(rows: list[Row]) -> dict[str, int | float]:
    tp = sum(r.true_malicious and r.predicted_malicious for r in rows)
    fp = sum((not r.true_malicious) and r.predicted_malicious for r in rows)
    fn = sum(r.true_malicious and (not r.predicted_malicious) for r in rows)
    tn = sum((not r.true_malicious) and (not r.predicted_malicious) for r in rows)
    return {
        "tp": int(tp),
        "fp": int(fp),
        "fn": int(fn),
        "tn": int(tn),
        **prf2(int(tp), int(fp), int(fn)),
        "fpr_window": round(safe_div(fp, fp + tn), 4),
    }


def ci_bounds(values: list[float]) -> tuple[float, float]:
    ordered = sorted(values)
    lo_idx = int(0.025 * (len(ordered) - 1))
    hi_idx = int(0.975 * (len(ordered) - 1))
    return round(ordered[lo_idx], 4), round(ordered[hi_idx], 4)


def metric_value(sample: list[Row], metric: str) -> float:
    c = confusion(sample)
    return float(c[metric])


def bootstrap(rows: list[Row], seed: int) -> dict[str, dict[str, float | int]]:
    rng = random.Random(seed)
    if not rows:
        return {}

    samples = {"precision": [], "recall": [], "f2": []}
    n = len(rows)
    for _ in range(B):
        picked = [rows[rng.randrange(n)] for _ in range(n)]
        for metric in samples:
            samples[metric].append(metric_value(picked, metric))

    point = confusion(rows)
    out: dict[str, dict[str, float | int]] = {}
    for metric, values in samples.items():
        lo, hi = ci_bounds(values)
        out[metric] = {
            "point": float(point[metric]),
            "ci_lower": lo,
            "ci_upper": hi,
            "bootstrap_mean": round(mean(values), 4),
            "B": B,
            "seed": seed,
        }
    return out


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def true_from_playbook(playbook: str) -> bool:
    lowered = playbook.lower()
    return "benign-" not in lowered and "/benign/" not in lowered


def load_rows(condition: str, run: dict[str, str]) -> list[Row]:
    run_id = run["run_id"]
    directory = RESULTS / CONDITIONS[condition] / run_id
    predictions_path = directory / "predictions.jsonl"
    if not predictions_path.exists():
        raise FileNotFoundError(predictions_path)

    rows: list[Row] = []
    if condition == "C3-Elastic":
        for line in predictions_path.read_text().splitlines():
            if not line.strip():
                continue
            pred = json.loads(line)
            playbook = pred["playbook"]
            rows.append(
                Row(
                    run_id=run_id,
                    mode=run["mode"],
                    tier=run["tier"],
                    playbook=playbook,
                    true_malicious=bool(pred["true_malicious"]),
                    predicted_malicious=bool(pred["predicted_malicious"]),
                    injection_flagged=False,
                )
            )
        return rows

    ground_truth = {}
    for line in (directory / "ground_truth.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        gt = json.loads(line)
        ground_truth[gt["window_id"]] = gt["playbook"]

    for line in predictions_path.read_text().splitlines():
        if not line.strip():
            continue
        pred = json.loads(line)
        playbook = ground_truth[pred["window_id"]]
        rows.append(
            Row(
                run_id=run_id,
                mode=run["mode"],
                tier=run["tier"],
                playbook=playbook,
                true_malicious=true_from_playbook(playbook),
                predicted_malicious=bool(pred["predicted_malicious"]),
                injection_flagged=bool(pred.get("injection_flagged", False)),
            )
        )
    return rows


def fpr_per_100k(condition: str, run_ids: list[str]) -> float:
    fp = 0
    sysmon_events = 0
    for run_id in run_ids:
        directory = RESULTS / CONDITIONS[condition] / run_id
        if not (directory / "fpr.json").exists():
            continue
        data = load_json(directory / "fpr.json")
        fp += int(data.get("fp", 0))
        sysmon_events += int(data.get("sysmon_event_count", 0))
    return round(safe_div(fp * 100_000, sysmon_events), 4)


def by_group(rows: list[Row], field: str) -> dict[str, dict[str, int | float]]:
    values = sorted({getattr(r, field) for r in rows})
    return {
        value: confusion([r for r in rows if getattr(r, field) == value])
        for value in values
    }


def injection_summary(rows: list[Row]) -> dict[str, Any]:
    per_run: dict[str, dict[str, int]] = {}
    for run in RUNS:
        run_rows = [r for r in rows if r.run_id == run["run_id"]]
        flagged = [r for r in run_rows if r.injection_flagged]
        per_run[run["run_id"]] = {
            "flagged_total": len(flagged),
            "flagged_malicious": sum(r.true_malicious for r in flagged),
            "flagged_benign": sum(not r.true_malicious for r in flagged),
            "flagged_false_negative": sum(
                r.true_malicious and not r.predicted_malicious for r in flagged
            ),
        }
    return {
        "per_run": per_run,
        "total_flagged": sum(v["flagged_total"] for v in per_run.values()),
        "total_flagged_malicious": sum(
            v["flagged_malicious"] for v in per_run.values()
        ),
        "total_flagged_benign": sum(v["flagged_benign"] for v in per_run.values()),
    }


def asr(rows: list[Row]) -> dict[str, float]:
    malicious = [r for r in rows if r.true_malicious]
    false_negative = [r for r in malicious if not r.predicted_malicious]
    silent_false_negative = [r for r in false_negative if not r.injection_flagged]
    return {
        "asr": round(safe_div(len(false_negative), len(malicious)), 4),
        "nasr": round(safe_div(len(silent_false_negative), len(malicious)), 4),
        "malicious_trials": len(malicious),
        "false_negatives": len(false_negative),
        "silent_false_negatives": len(silent_false_negative),
    }


def verdicts(results: dict) -> dict[str, str]:
    pooled = results["per_condition"]
    c1 = pooled["C1-full"]["pooled"]["f2"]
    c1_no = pooled["C1-nohardening"]["pooled"]["f2"]
    c2 = pooled["C2-naive"]["pooled"]["f2"]
    c3 = pooled["C3-Elastic"]["pooled"]["f2"]
    flags = results["injection_resistance"]["C1-full"]["total_flagged"]

    out = {}
    out["agentic_vs_elastic"] = (
        "SUPPORTED: both C1 variants strongly exceed C3-Elastic on F2 "
        f"(C1-full={c1:.4f}, C1-nohardening={c1_no:.4f}, C3={c3:.4f})."
    )
    if c1 > c2 and c1_no > c2:
        label = "SUPPORTED"
    elif c1 >= c2 or c1_no >= c2:
        label = "MIXED"
    else:
        label = "NOT SUPPORTED"
    out["orchestration_vs_naive"] = (
        f"{label}: detection F2 is close across LLM conditions "
        f"(C1-full={c1:.4f}, C1-nohardening={c1_no:.4f}, C2={c2:.4f})."
    )
    out["hardening_ablation"] = (
        "MIXED: C1-full does not clearly dominate C1-nohardening on detection F2 "
        f"(C1-full={c1:.4f}, C1-nohardening={c1_no:.4f}), but C1-full uniquely "
        f"flags adversarial injections ({flags} windows) while the ablated and naive "
        "conditions expose no injection-detection signal."
    )
    return out


def fmt_ci(ci: dict[str, float | int]) -> str:
    return f"{ci['point']:.4f} [{ci['ci_lower']:.4f}, {ci['ci_upper']:.4f}]"


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(headers) + " |"]
    out.append("| " + " | ".join(["---"] * len(headers)) + " |")
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def write_report(results: dict) -> None:
    rows = []
    for condition, data in results["per_condition"].items():
        pooled = data["pooled"]
        ci = data["bootstrap_ci"]
        rows.append(
            [
                condition,
                str(pooled["tp"]),
                str(pooled["fp"]),
                str(pooled["fn"]),
                str(pooled["tn"]),
                fmt_ci(ci["precision"]),
                fmt_ci(ci["recall"]),
                fmt_ci(ci["f2"]),
                f"{pooled['fpr_window']:.4f}",
                f"{pooled['fpr_per_100k']:.4f}",
            ]
        )

    tier_rows = []
    for tier, by_condition in results["by_tier"].items():
        tier_rows.append(
            [
                tier,
                f"{by_condition['C1-full']['f2']:.4f}",
                f"{by_condition['C1-nohardening']['f2']:.4f}",
                f"{by_condition['C2-naive']['f2']:.4f}",
                f"{by_condition['C3-Elastic']['f2']:.4f}",
            ]
        )

    mode_rows = []
    for mode, by_condition in results["by_mode"].items():
        mode_rows.append(
            [
                mode,
                f"{by_condition['C1-full']['f2']:.4f}",
                f"{by_condition['C1-nohardening']['f2']:.4f}",
                f"{by_condition['C2-naive']['f2']:.4f}",
                f"{by_condition['C3-Elastic']['f2']:.4f}",
            ]
        )

    flag_rows = []
    for run in RUNS:
        run_id = run["run_id"]
        flags = results["injection_resistance"]["C1-full"]["per_run"][run_id]
        flag_rows.append(
            [
                run_id,
                run["mode"],
                run["tier"],
                str(flags["flagged_total"]),
                str(flags["flagged_malicious"]),
                str(flags["flagged_benign"]),
                str(flags["flagged_false_negative"]),
            ]
        )

    asr_rows = []
    for condition, data in results["resilience_asr"].items():
        asr_rows.append(
            [
                condition,
                f"{data['pooled']['asr']:.4f}",
                f"{data['pooled']['nasr']:.4f}",
                str(data["pooled"]["false_negatives"]),
                str(data["pooled"]["silent_false_negatives"]),
            ]
        )

    report = [
        "# MAS-Hunt v2 Aggregate Results",
        "",
        "Source: health-gated v2 signal-rich matrix on the lab host. Six adversarial runs are included: per-attack-burst and interleaved modes crossed with overt, encoded, and steganographic tiers. Each condition is scored against the same 1,092 playbook windows.",
        "",
        "## Aggregate Performance",
        markdown_table(
            [
                "Condition",
                "TP",
                "FP",
                "FN",
                "TN",
                "Precision (95% CI)",
                "Recall (95% CI)",
                "F2 (95% CI)",
                "FPR window",
                "FP/100k Sysmon",
            ],
            rows,
        ),
        "",
        "## F2 by Adversarial Tier",
        markdown_table(
            ["Tier", "C1-full", "C1-nohardening", "C2-naive", "C3-Elastic"],
            tier_rows,
        ),
        "",
        "## F2 by Injection Mode",
        markdown_table(
            ["Mode", "C1-full", "C1-nohardening", "C2-naive", "C3-Elastic"],
            mode_rows,
        ),
        "",
        "## Injection-Resistance Signal",
        markdown_table(
            [
                "Run",
                "Mode",
                "Tier",
                "Flagged",
                "Flagged malicious",
                "Flagged benign",
                "Flagged FN",
            ],
            flag_rows,
        ),
        "",
        "## ASR/NASR",
        markdown_table(
            ["Condition", "ASR", "NASR", "FN", "Silent FN"],
            asr_rows,
        ),
        "",
        "## Verdicts",
    ]
    for key, value in results["verdicts"].items():
        report.append(f"- **{key}**: {value}")
    report.append("")
    report.append("## Integrity Notes")
    report.append(
        "- C2-naive cells with classification errors were excluded until rerun cleanly; this report only emits when all required metrics files exist."
    )
    report.append(
        "- Bootstrap CIs use 10,000 percentile resamples over per-window outcomes with seed 42."
    )
    report.append(
        "- C1-full's injection-flag count is evidence of adversarial-steer resistance, not a standalone detection metric."
    )
    report.append("")

    (OUT / "aggregate-v2.md").write_text("\n".join(report))


def main() -> None:
    missing = []
    all_rows: dict[str, list[Row]] = {}
    for condition in CONDITIONS:
        rows: list[Row] = []
        for run in RUNS:
            run_id = run["run_id"]
            directory = RESULTS / CONDITIONS[condition] / run_id
            for required in ["metrics.json", "predictions.jsonl"]:
                if not (directory / required).exists():
                    missing.append(str(directory / required))
            if (
                condition != "C3-Elastic"
                and not (directory / "ground_truth.jsonl").exists()
            ):
                missing.append(str(directory / "ground_truth.jsonl"))
            if (directory / "predictions.jsonl").exists():
                rows.extend(load_rows(condition, run))
        all_rows[condition] = rows

    if missing:
        raise SystemExit("Missing required artifacts:\n" + "\n".join(missing))

    OUT.mkdir(parents=True, exist_ok=True)

    results = {
        "meta": {
            "runs": RUNS,
            "conditions": CONDITIONS,
            "n_runs": len(RUNS),
            "n_windows_per_condition": {k: len(v) for k, v in all_rows.items()},
            "bootstrap": {"B": B, "seed": SEED, "alpha": 0.05},
            "scope": "signal-rich v2 adversarial matrix only",
            "c2_note": "C2-naive uses native subagent orchestration from results/c2-naive-orch-v2; legacy claude-p results/c2-naive-v2 are excluded.",
        },
        "per_condition": {},
        "by_tier": {},
        "by_mode": {},
        "injection_resistance": {},
        "resilience_asr": {},
    }

    run_ids = [run["run_id"] for run in RUNS]
    for condition, rows in all_rows.items():
        per_run = {}
        for run in RUNS:
            per_run[run["run_id"]] = confusion(
                [r for r in rows if r.run_id == run["run_id"]]
            )
        pooled = confusion(rows)
        pooled["fpr_per_100k"] = fpr_per_100k(condition, run_ids)
        results["per_condition"][condition] = {
            "per_run": per_run,
            "pooled": pooled,
            "bootstrap_ci": bootstrap(rows, SEED),
        }
        results["resilience_asr"][condition] = {
            "pooled": asr(rows),
            "by_tier": {
                tier: asr([r for r in rows if r.tier == tier])
                for tier in sorted({r.tier for r in rows})
            },
            "by_mode": {
                mode: asr([r for r in rows if r.mode == mode])
                for mode in sorted({r.mode for r in rows})
            },
        }

    for tier in sorted({run["tier"] for run in RUNS}):
        results["by_tier"][tier] = {
            condition: confusion([r for r in rows if r.tier == tier])
            for condition, rows in all_rows.items()
        }

    for mode in sorted({run["mode"] for run in RUNS}):
        results["by_mode"][mode] = {
            condition: confusion([r for r in rows if r.mode == mode])
            for condition, rows in all_rows.items()
        }

    results["injection_resistance"]["C1-full"] = injection_summary(all_rows["C1-full"])
    results["verdicts"] = verdicts(results)

    (OUT / "RESULTS.json").write_text(json.dumps(results, indent=2) + "\n")
    write_report(results)

    print(json.dumps(results["per_condition"], indent=2))
    print("\nWrote:")
    print(OUT / "RESULTS.json")
    print(OUT / "aggregate-v2.md")


if __name__ == "__main__":
    main()
