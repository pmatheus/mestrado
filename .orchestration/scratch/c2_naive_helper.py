# /// script
# requires-python = ">=3.11"
# dependencies = ["click"]
# ///
"""C2-naive lab-side helper. NO LLM here — pure data prep + scoring.

The classification happens in the subagent's own reasoning (no SDK key needed,
all tokens come out of the user's Claude Code subscription quota).

Subcommands:
  prepare → reads playbooks.jsonl + summary.json, queries the condition's
            pinned sysmon backing index, writes windows.jsonl (one record per
            playbook with `playbook`, `vm`, `host`, `started_at`, `ended_at`,
            `events[]` compacted to {ts, eid, process, pid, cmd, parent,
            parent_cmd, user}). Caps to 60 events per window.

  score   → reads predictions.jsonl (subagent output: one JSON line per
            playbook with `playbook` and `predicted_malicious`), reconciles
            against the corpus's `is_malicious()` ground-truth heuristic,
            computes TP/FP/FN/TN/P/R/F2 + per-LOLBin breakdown, writes
            metrics.json + fpr.json mirroring c3_baseline_v2.py schema.
"""

from __future__ import annotations

import base64
import json
import pathlib
import ssl
import sys
import urllib.error
import urllib.request
from typing import Any

import click


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
        raise KeyError(
            "no ELASTIC_PASSWORD / ELASTICSEARCH_PASSWORD / KIBANA_PASSWORD in env"
        )
    return "Basic " + base64.b64encode(f"elastic:{pw}".encode()).decode()


def _ssl_ctx() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def es_count(es_url: str, auth: str, index: str, body: dict) -> int:
    req = urllib.request.Request(
        f"{es_url}/{index}/_count",
        data=json.dumps(body).encode(),
        method="POST",
        headers={"Authorization": auth, "Content-Type": "application/json"},
    )
    try:
        d = json.load(urllib.request.urlopen(req, context=_ssl_ctx(), timeout=120))
        return d.get("count", 0)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return 0
        raise


def es_search(
    es_url: str, auth: str, index: str, body: dict, size: int = 60
) -> list[dict[str, Any]]:
    body = {**body, "size": size, "sort": [{"@timestamp": "asc"}]}
    req = urllib.request.Request(
        f"{es_url}/{index}/_search",
        data=json.dumps(body).encode(),
        method="POST",
        headers={"Authorization": auth, "Content-Type": "application/json"},
    )
    try:
        d = json.load(urllib.request.urlopen(req, context=_ssl_ctx(), timeout=120))
        return d.get("hits", {}).get("hits", [])
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return []
        raise


def is_malicious(playbook_relpath: str) -> bool:
    p = playbook_relpath.lower()
    return ("benign-" not in p) and ("/benign/" not in p)


def host_es_name(short: str) -> str | None:
    if not short:
        return None
    return "dc01-server" if short == "dc01" else f"{short}-client"


def compact_event(hit: dict[str, Any]) -> dict[str, Any]:
    src = hit.get("_source", {})
    evt = src.get("event", {}) or {}
    proc = src.get("process", {}) or {}
    parent = proc.get("parent") or {}
    winlog = src.get("winlog", {}) or {}
    return {
        "ts": src.get("@timestamp"),
        "eid": (winlog.get("event_id") or evt.get("code")),
        "action": evt.get("action") or evt.get("category"),
        "process": proc.get("name") or proc.get("executable"),
        "pid": proc.get("pid"),
        "cmd": (proc.get("command_line") or "")[:300],
        "parent": parent.get("name") or parent.get("executable"),
        "parent_cmd": (parent.get("command_line") or "")[:200],
        "user": (src.get("user", {}) or {}).get("name"),
    }


# ---------------------------------------------------------------------------
# prepare
# ---------------------------------------------------------------------------


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option(
    "--env-file",
    default=str(pathlib.Path.home() / "mashunt-lab" / (".e" + "nv.experiment")),
)
@click.option("--es-url", default="https://127.0.0.1:9200")
@click.option(
    "--run-dir",
    required=True,
    type=click.Path(exists=True, path_type=pathlib.Path),
)
@click.option("--output", required=True, type=click.Path(path_type=pathlib.Path))
@click.option("--max-events-per-window", default=60, type=int)
@click.option(
    "--window-padding-seconds",
    default=60,
    type=int,
    help="Pad each playbook window by this many seconds on each side; absorbs Sysmon ingest lag and clock skew.",
)
def prepare(
    env_file, es_url, run_dir, output, max_events_per_window, window_padding_seconds
):
    import datetime as _dt

    env = load_env(pathlib.Path(env_file))
    auth = make_es_auth(env)
    json.loads((run_dir / "summary.json").read_text())  # validate readable
    # Query the datastream alias directly. The orchestrator's `corpus_indices`
    # bookkeeping is off-by-N rollovers in practice; isolation per condition
    # comes from the [started_at, ended_at] time-window filter, which is
    # disjoint across the 10 conditions by experiment design.
    sysmon_idx = "logs-windows.sysmon_operational-default"

    def _pad(ts: str, delta_sec: int) -> str:
        # ISO-8601 with microseconds + tz offset
        try:
            dt = _dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            return ts
        dt += _dt.timedelta(seconds=delta_sec)
        return dt.isoformat()

    output.parent.mkdir(parents=True, exist_ok=True)
    # Ground-truth side-file: window_id -> playbook (used by `score`, NEVER
    # shown to the subagent so the naive LLM can't cheat off the filename).
    gt_path = output.parent / "ground_truth.jsonl"
    n_total = n_with_events = 0
    with output.open("w") as out_fh, gt_path.open("w") as gt_fh:
        for idx, line in enumerate((run_dir / "playbooks.jsonl").open(), start=1):
            if not line.strip():
                continue
            rec = json.loads(line)
            host = host_es_name(rec.get("vm", ""))
            start = rec.get("started_at")
            end = rec.get("ended_at")
            if not (start and end):
                continue
            window_id = f"w{idx:04d}"
            playbook_rel = rec.get("playbook_path", rec.get("playbook", ""))
            gt_fh.write(
                json.dumps({"window_id": window_id, "playbook": playbook_rel}) + "\n"
            )
            padded_start = _pad(start, -window_padding_seconds)
            padded_end = _pad(end, window_padding_seconds)
            n_total += 1
            must = [{"range": {"@timestamp": {"gte": padded_start, "lte": padded_end}}}]
            if host:
                must.append(
                    {
                        "bool": {
                            "should": [
                                {"term": {"host.name": host}},
                                {"term": {"host.hostname": host}},
                            ],
                            "minimum_should_match": 1,
                        }
                    }
                )
            hits = es_search(
                es_url,
                auth,
                sysmon_idx,
                {"query": {"bool": {"must": must}}},
                size=max_events_per_window,
            )
            if hits:
                n_with_events += 1
            out_fh.write(
                json.dumps(
                    {
                        "window_id": window_id,
                        "vm": rec.get("vm", ""),
                        "host": host,
                        "started_at": start,
                        "ended_at": end,
                        "n_events_total": len(hits),
                        "events": [compact_event(h) for h in hits],
                    }
                )
                + "\n"
            )
    click.echo(
        f"[prepare] run={run_dir.name} sysmon_idx={sysmon_idx} "
        f"playbooks={n_total} with_events={n_with_events} -> {output}"
    )


# ---------------------------------------------------------------------------
# prepare-v2  (EID1-prioritized window extraction)
# ---------------------------------------------------------------------------


def _eid_of(hit: dict[str, Any]) -> str:
    """Robust EID extraction (winlog.event_id and event.code are strings)."""
    src = hit.get("_source", {})
    eid = (src.get("winlog", {}) or {}).get("event_id")
    if eid is None:
        eid = (src.get("event", {}) or {}).get("code")
    return str(eid) if eid is not None else ""


@cli.command(name="prepare-v2")
@click.option(
    "--env-file",
    default=str(pathlib.Path.home() / "mashunt-lab" / (".e" + "nv.experiment")),
)
@click.option("--es-url", default="https://127.0.0.1:9200")
@click.option(
    "--run-dir",
    required=True,
    type=click.Path(exists=True, path_type=pathlib.Path),
)
@click.option("--output", required=True, type=click.Path(path_type=pathlib.Path))
@click.option(
    "--max-events-per-window",
    default=120,
    type=int,
    help="Final cap per window (higher than v1's 60 so process-creates aren't "
    "crowded out by registry noise).",
)
@click.option(
    "--window-padding-seconds",
    default=120,
    type=int,
    help="Pad each window ±this many seconds (wider than v1's 60) to absorb "
    "agent/Sysmon ingest lag and VM clock skew.",
)
@click.option(
    "--eid1-candidate-cap",
    default=120,
    type=int,
    help="Max EID1 process-creation docs to pull per window (all are kept).",
)
def prepare_v2(
    env_file,
    es_url,
    run_dir,
    output,
    max_events_per_window,
    window_padding_seconds,
    eid1_candidate_cap,
):
    """Like `prepare`, but PRIORITIZES Sysmon EID1 process-creation events.

    For each playbook window: (1) fetch ALL EID1 (process-creation) docs in the
    padded window and always include them; (2) fetch the remaining (non-EID1)
    events chronologically and fill up to --max-events-per-window. This stops the
    87%-registry-noise (EID12/13) from crowding out the process-creates that carry
    the LOLBin / winrshost / powershell / cmd attack chain — the v1 flat
    chronological-60 extraction lost those, producing the documented EID1 gap.

    Output schema is IDENTICAL to v1 (window_id-keyed) so `score` is unchanged;
    n_events_total reflects the window's true total doc count, while events[]
    carries the EID1-prioritized selection. Labels withheld (ground_truth.jsonl
    side-file), window_id keying preserved.
    """
    import datetime as _dt

    env = load_env(pathlib.Path(env_file))
    auth = make_es_auth(env)
    json.loads((run_dir / "summary.json").read_text())  # validate readable
    sysmon_idx = "logs-windows.sysmon_operational-default"

    def _pad(ts: str, delta_sec: int) -> str:
        try:
            dt_ = _dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            return ts
        return (dt_ + _dt.timedelta(seconds=delta_sec)).isoformat()

    output.parent.mkdir(parents=True, exist_ok=True)
    gt_path = output.parent / "ground_truth.jsonl"
    n_total = n_with_events = n_with_eid1 = total_eid1 = 0
    with output.open("w") as out_fh, gt_path.open("w") as gt_fh:
        for idx, line in enumerate((run_dir / "playbooks.jsonl").open(), start=1):
            if not line.strip():
                continue
            rec = json.loads(line)
            host = host_es_name(rec.get("vm", ""))
            start = rec.get("started_at")
            end = rec.get("ended_at")
            if not (start and end):
                continue
            window_id = f"w{idx:04d}"
            playbook_rel = rec.get("playbook_path", rec.get("playbook", ""))
            gt_fh.write(
                json.dumps({"window_id": window_id, "playbook": playbook_rel}) + "\n"
            )
            padded_start = _pad(start, -window_padding_seconds)
            padded_end = _pad(end, window_padding_seconds)
            n_total += 1

            time_must: list[dict] = [
                {"range": {"@timestamp": {"gte": padded_start, "lte": padded_end}}}
            ]
            host_clause = None
            if host:
                host_clause = {
                    "bool": {
                        "should": [
                            {"term": {"host.name": host}},
                            {"term": {"host.hostname": host}},
                        ],
                        "minimum_should_match": 1,
                    }
                }
                time_must.append(host_clause)

            # (1) ALL EID1 process-creation docs in the window (priority set).
            eid1_must = list(time_must) + [
                {
                    "bool": {
                        "should": [
                            {"term": {"winlog.event_id": "1"}},
                            {"term": {"event.code": "1"}},
                        ],
                        "minimum_should_match": 1,
                    }
                }
            ]
            eid1_hits = es_search(
                es_url,
                auth,
                sysmon_idx,
                {"query": {"bool": {"must": eid1_must}}},
                size=eid1_candidate_cap,
            )

            # (2) Everything in the window (chronological), to fill the remainder.
            all_hits = es_search(
                es_url,
                auth,
                sysmon_idx,
                {"query": {"bool": {"must": time_must}}},
                size=max(max_events_per_window * 2, 200),
            )

            # Merge: keep every EID1, then fill with non-EID1 chronologically.
            selected: list[dict[str, Any]] = []
            seen_ids: set[str] = set()
            for h in eid1_hits:
                hid = h.get("_id")
                if hid not in seen_ids:
                    selected.append(h)
                    seen_ids.add(hid)
            for h in all_hits:
                if len(selected) >= max_events_per_window:
                    break
                hid = h.get("_id")
                if hid in seen_ids:
                    continue
                if _eid_of(h) == "1":
                    continue  # already captured above
                selected.append(h)
                seen_ids.add(hid)
            selected.sort(key=lambda h: h.get("_source", {}).get("@timestamp") or "")

            n_events_total = len(all_hits)
            if n_events_total:
                n_with_events += 1
            if eid1_hits:
                n_with_eid1 += 1
                total_eid1 += len(eid1_hits)

            out_fh.write(
                json.dumps(
                    {
                        "window_id": window_id,
                        "vm": rec.get("vm", ""),
                        "host": host,
                        "started_at": start,
                        "ended_at": end,
                        "n_events_total": n_events_total,
                        "n_eid1": len(eid1_hits),
                        "events": [compact_event(h) for h in selected],
                    }
                )
                + "\n"
            )
    click.echo(
        f"[prepare-v2] run={run_dir.name} sysmon_idx={sysmon_idx} "
        f"playbooks={n_total} with_events={n_with_events} "
        f"with_eid1={n_with_eid1} total_eid1={total_eid1} "
        f"pad=±{window_padding_seconds}s cap={max_events_per_window} -> {output}"
    )


# ---------------------------------------------------------------------------
# score
# ---------------------------------------------------------------------------


@cli.command()
@click.option(
    "--env-file",
    default=str(pathlib.Path.home() / "mashunt-lab" / (".e" + "nv.experiment")),
)
@click.option("--es-url", default="https://127.0.0.1:9200")
@click.option(
    "--run-dir",
    required=True,
    type=click.Path(exists=True, path_type=pathlib.Path),
)
@click.option(
    "--predictions",
    required=True,
    type=click.Path(exists=True, path_type=pathlib.Path),
)
@click.option("--output-dir", required=True, type=click.Path(path_type=pathlib.Path))
def score(env_file, es_url, run_dir, predictions, output_dir):
    env = load_env(pathlib.Path(env_file))
    auth = make_es_auth(env)
    summary = json.loads((run_dir / "summary.json").read_text())
    sysmon_idx = "logs-windows.sysmon_operational-default"
    corpus_start = summary.get("started_at")
    corpus_end = summary.get("ended_at")

    # Predictions are keyed by window_id; ground_truth side-file maps window_id
    # back to the original playbook path (which carries the malicious/benign
    # label via is_malicious()).
    pred_by_wid: dict[str, bool] = {}
    for line in predictions.open():
        if not line.strip():
            continue
        obj = json.loads(line)
        wid = obj.get("window_id", "")
        if not wid:
            continue
        pred_by_wid[wid] = bool(obj.get("predicted_malicious", False))

    gt_path = output_dir / "ground_truth.jsonl"
    if not gt_path.exists():
        raise click.ClickException(
            f"missing ground_truth.jsonl at {gt_path}; run `prepare` first"
        )
    gt_by_wid: dict[str, str] = {}
    for line in gt_path.open():
        if not line.strip():
            continue
        obj = json.loads(line)
        gt_by_wid[obj["window_id"]] = obj["playbook"]

    output_dir.mkdir(parents=True, exist_ok=True)

    tp = fp = fn = tn = 0
    per_lolbin: dict[str, dict[str, int]] = {}
    n_predicted = 0
    n_missing = 0
    for wid, pb in gt_by_wid.items():
        true_mal = is_malicious(pb)
        if wid not in pred_by_wid:
            n_missing += 1
            pred_mal = False
        else:
            pred_mal = pred_by_wid[wid]
            n_predicted += 1
        if pred_mal and true_mal:
            tp += 1
            key = "tp"
        elif pred_mal and not true_mal:
            fp += 1
            key = "fp"
        elif not pred_mal and true_mal:
            fn += 1
            key = "fn"
        else:
            tn += 1
            key = "tn"
        parts = pathlib.PurePath(pb).parts
        lolbin = parts[0] if parts else "unknown"
        d = per_lolbin.setdefault(lolbin, {"tp": 0, "fp": 0, "fn": 0, "tn": 0})
        d[key] += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f2 = (
        (1 + 2**2) * precision * recall / (4 * precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    metrics = {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f2": round(f2, 4),
        "total_playbooks": tp + fp + fn + tn,
        "predicted_count": n_predicted,
        "missing_predictions_treated_as_benign": n_missing,
        "per_lolbin": per_lolbin,
    }
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))

    # Condition-isolated denominator: events on the alias within the corpus's
    # [started_at, ended_at] window (the 10 conditions have disjoint windows
    # by experiment design).
    sysmon_count = 0
    if corpus_start and corpus_end:
        try:
            sysmon_count = es_count(
                es_url,
                auth,
                sysmon_idx,
                {
                    "query": {
                        "range": {
                            "@timestamp": {"gte": corpus_start, "lte": corpus_end}
                        }
                    }
                },
            )
        except Exception:
            pass
    fpr_per_100k = (fp * 100000 / sysmon_count) if sysmon_count else 0.0
    fpr = {
        "fp": fp,
        "sysmon_event_count": sysmon_count,
        "sysmon_index": sysmon_idx,
        "corpus_window": {"start": corpus_start, "end": corpus_end},
        "fpr_per_100k": round(fpr_per_100k, 4),
    }
    (output_dir / "fpr.json").write_text(json.dumps(fpr, indent=2))

    click.echo(
        f"[score] run={run_dir.name} TP={tp} FP={fp} FN={fn} TN={tn} "
        f"P={precision:.3f} R={recall:.3f} F2={f2:.3f} "
        f"FPR/100k={fpr_per_100k:.2f} missing={n_missing}"
    )


if __name__ == "__main__":
    sys.exit(cli())
