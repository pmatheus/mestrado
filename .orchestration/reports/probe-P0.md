# PROBE P0 — Cost Probe (go/no-go gate for MAS-Hunt C1-full)

**Worker**: general-purpose (P0)  **Date**: 2026-05-28  **Lab**: `/home/user/mashunt-lab` (LAB_BASE pinned)
**Control run used**: `20260527T215714Z-ba30c6` (mode=none, tier=mixed)

---

## 1. `c2_naive_helper.py` prepare/score contract

File: `/home/user/mashunt-lab/scripts/eval/c2_naive_helper.py` (~450 lines, click group, deps=`click`).
Docstring is explicit: **"NO LLM here — pure data prep + scoring. The classification happens in the subagent's own reasoning."** Env file default `~/mashunt-lab/.env.experiment` (ELASTIC_PASSWORD). ES default `https://127.0.0.1:9200`. Sysmon index hard-pinned to the datastream alias `logs-windows.sysmon_operational-default` (NOT `corpus_indices` — isolation is by the disjoint `[started_at,ended_at]` time window).

### `prepare`
- **Inputs**: `--run-dir` (needs `summary.json` + `playbooks.jsonl`), `--output <windows.jsonl>`, `--max-events-per-window` (default 60), `--window-padding-seconds` (default 60, pads both sides to absorb ingest lag).
- **Process**: iterate `playbooks.jsonl` (idx from 1); `window_id=f"w{idx:04d}"`; map vm→host (`dc01`→`dc01-server`, else `{vm}-client`); ES `_search` on the sysmon alias filtered by padded time-range + `host.name|host.hostname`, size=60, sort `@timestamp asc`; compact each hit to `{ts, eid, action, process, pid, cmd[:300], parent, parent_cmd[:200], user}`.
- **Outputs**:
  - `windows.jsonl` — one record per playbook: `{window_id, vm, host, started_at, ended_at, n_events_total, events[]}`. **Playbook path is deliberately NOT included** (anti-cheat).
  - `ground_truth.jsonl` (side-file, same dir as `--output`) — `{window_id, playbook}`. Used only by `score`, never shown to the analyst.
- **KEY: the join key is `window_id`, NOT (playbook,vm,started_at).** Predictions must carry `window_id`. (The task brief's "playbook/vm/started_at/ended_at" schema is the C3 schema; the C1/C2 helper schema is `window_id`-keyed.)

### `score`
- **Inputs**: `--run-dir` (summary.json → corpus_start/end for FPR denominator), `--predictions <predictions.jsonl>`, `--output-dir`.
- **Predictions schema consumed**: `{"window_id": "...", "predicted_malicious": bool}` (extra fields like `confidence`/`reasoning` are ignored but allowed). Missing window_id → treated as benign.
- **Ground truth**: reads `ground_truth.jsonl` **from `--output-dir`** (must be placed there first); `is_malicious(path) = ("benign-" not in path.lower()) and ("/benign/" not in path.lower())`.
- **Outputs**:
  - `metrics.json` — `{tp,fp,fn,tn, precision, recall, f2, total_playbooks, predicted_count, missing_predictions_treated_as_benign, per_lolbin{lolbin:{tp,fp,fn,tn}}}`. P=tp/(tp+fp), R=tp/(tp+fn), F2=5·P·R/(4P+R); all default to 0.0 when denominator is 0. `per_lolbin` keyed by first path component.
  - `fpr.json` — `{fp, sysmon_event_count, sysmon_index, corpus_window, fpr_per_100k}`; denominator = ES `_count` of sysmon docs in `[corpus_start,corpus_end]`.

---

## 2. C2-naive prediction generation: **HEURISTIC, not LLM** (definitive)

**Answer: the shipped May C2-naive AND C1-nohardening predictions were produced by a deterministic Python heuristic — NO LLM pass, zero tokens.**

Evidence (all reproduced this run):
1. `results/_archive-2026-05/c2-naive/SUMMARY.md` records **`tok_in = 0`, `tok_out = 0` for ALL 10 runs**, and "Total input tokens: 0 / Total output tokens: 0".
2. Reasoning strings in archived `predictions.jsonl` are **templated f-strings**, not prose:
   - C2: `"only background OS processes (n=7, EIDs={'12': 7})"`, `"{k} WmiPrvSE.exe spawn — possible WMI execution"`, `"LOLBin process(es) present: sdbinst.exe"`.
   - C1-nohard: `"M3{board:priorities=lolbin,lateral,credential,privesc} | M3{manager→Worker-B batch by host=ws01-client} | M3{Worker-B verdict: BENIGN score=0.00 | no Board-priority signals across 7 events}"`.
3. `confidence` collapses to a tiny discrete set (C2: 0.55/0.6/0.7/0.9; C1-nohard: 0.55/0.9) — signature of branch-assigned constants, not model output.
4. No `agent.log` / token-usage file exists in any archive run dir.
5. A `classify_one(client: anthropic.AsyncAnthropic, ... NAIVE_SYSTEM_PROMPT ...)` API path *exists in the May session code* but was **never the shipped path** (it would have logged tokens; SUMMARY shows 0). The templated heuristic is what actually wrote the archive.

**Implication for the experiment**: C2-naive and C1-nohardening can be reproduced for the new runs at **near-zero LLM cost** by re-running their heuristic over the new `windows.jsonl`. Only **C1-full** requires a genuine LLM analyst pass. This collapses total LLM cost to "C1-full only".

> Caveat / honesty flag for the dissertation: if the paper claims C2-naive is a "single-pass LLM baseline", that claim is not supported by the archived artifacts (tok=0, templated). Either (a) re-run C2-naive as a real bare-prompt LLM pass for parity with C1-full, or (b) re-frame C2/C1-nohard as deterministic-heuristic ablations. The orchestrator must decide; flagged explicitly.

---

## 3. Smoke metrics.json (10-playbook subset, control run)

`prepare` ran clean: `playbooks=182 with_events=105` in **6.6s**. First 10 windows classified by me (the LLM analyst) applying C1-full M1-M5+M3 (OBSERVE→HYPOTHESIZE→EVIDENCE→CROSS-VALIDATE→CLASSIFY) **from telemetry only** (filename withheld):

```json
{ "tp": 0, "fp": 0, "fn": 6, "tn": 4,
  "precision": 0.0, "recall": 0.0, "f2": 0.0,
  "total_playbooks": 10, "predicted_count": 10,
  "missing_predictions_treated_as_benign": 0,
  "per_lolbin": { "bitsadmin": {"tp":0,"fp":0,"fn":6,"tn":4} } }
```
`fpr.json`: fp=0, sysmon_event_count=1,922,286 (corpus window), fpr_per_100k=0.0.

GT for w0001-w0010 = 4 benign (bitsadmin/benign-*) + 6 malicious (bitsadmin-mal-*). I classified all 10 **benign** — honest given the telemetry: the 6 malicious windows contained ONLY OS-maintenance/registry noise (MoUsoCoreWorker, svchost, lsass-registry, AppHostRegistrationVerifier, CompatTelRunner) + 4 of them had **zero ingested events**. No bitsadmin.exe/cmd/powershell EID1 process-creation was present in any malicious window. This is the documented **EID1 LOLBin telemetry gap** (87% of corpus events are EID 12/13 registry; process-creates for LOLBins largely not captured), already noted in the May session and `project_sysmon_eid1_gap.md`. The single-window naive frame cannot recover the missing process_create context — exactly the signal-starved ceiling the dissertation predicts. **The pipeline is mechanically valid; the score is faithful to the telemetry.**

Artifacts on lab: `results/c1-full-smoke/20260527T215714Z-ba30c6/` → `windows.jsonl` (182), `windows.smoke.jsonl` (10), `ground_truth[.smoke].jsonl`, `analyst_verdicts.jsonl`, `predictions.jsonl`, `score-smoke/{metrics,fpr,ground_truth}.json`.

---

## 4. Measured per-window cost

**Telemetry footprint (hard measurement):**
- 10 smoke windows: 191 events, event-JSON = 37,761 chars ≈ **10,788 tokens** (event-heavy subset: 2 windows at the 60-event cap, 19.1 events/win).
- Full 182-window run: 2,114 events, event-JSON = 426,027 chars ≈ **121,722 tokens**, 105/182 windows non-empty. Average **≈ 670 telemetry tokens/window** across the full run (much lower than the smoke subset, which is front-loaded with the noisiest update windows).

**Per-window token budget for a real C1-full LLM call** (estimate, calibrated to this run):
- Input = telemetry (~670 avg, up to ~3.5k at the 60-event cap) + M1-M5 governance preamble (~700 tok, cacheable) + per-window framing (~150 tok) ≈ **~1.5k input tok/window** (amortized, with prompt caching on the preamble).
- Output = verdict JSON + reasoning (~120-200 tok/window, like my verdicts) ≈ **~180 output tok/window**.
- **≈ 1.7k total tokens/window** as a working figure (1.5k in / 0.2k out).

**Wall-time:** `prepare` 6.6s/run (one-time ES extract), `score` 0.24s/run (negligible). The cost driver is the **analyst reasoning turn**. As an interactive Claude Code agent batching windows, realistic throughput is **~25-40 windows per agent turn** before context pressure; budget **~0.3-0.5 min/window** of analyst wall-time when run as serialized subagent batches.

---

## 5. Full-scope extrapolation

Per run = 182 scorable windows (~105 with events; the 77 empty windows are ~free — trivial "no telemetry → benign").

| Scope | Windows | LLM tokens (C1-full only) | Analyst wall-time |
|---|---|---|---|
| 1 run, C1-full | 182 | ~182 × 1.7k ≈ **0.31M tok** | ~0.5-1.5 h (batched subagents) |
| 3 runs, C1-full | 546 | **~0.93M tok** | ~2-4 h |
| **C2-naive + C1-nohard re-score (heuristic)** | any | **~0 LLM tok** (deterministic) | seconds/run |
| Original brief's "3 cond × 3 runs all LLM" | 1,638 | ~2.8M tok | ~6-12 h |

Because **only C1-full needs an LLM** (finding #2), the effective LLM budget is just the C1-full column. The 3-conditions-×-3-runs framing in the task is an over-estimate: C2-naive and C1-nohardening are reproduced by re-running their heuristics over the new `windows.jsonl` at zero token cost.

---

## 6. RECOMMENDATION

**Go.** The C1-full pipeline works end-to-end on the new runs (prepare → analyst classify → score → valid metrics.json + fpr.json), verified on the control run.

**Recommended K = 3 C1-full runs** (matches plan E1 default): the control **none/mixed** (`20260527T215714Z-ba30c6`) + one mid adversarial (e.g. `pre-burst/encoded` `20260527T234443Z-bb41ce`) + one hard adversarial (`per-attack-burst/steganographic` `20260528T044122Z-225fc6` or `interleaved/steganographic` `20260528T091131Z-6bd91b`). 3 runs ≈ 0.9M tokens / a few hours — comfortably affordable. K=3 gives a baseline-vs-adversarial contrast and supports bootstrap CIs (A1). K could extend to all 10 later if the per-attack-burst/interleaved runs (which carry vastly more events: FPR denominators in the millions vs thousands) prove informative; but 3 is the right gated start.

**C2-naive / C1-nohardening: re-run the HEURISTIC over the SAME 3 runs' windows.jsonl — zero LLM cost.** This is faithful to how May produced them and keeps conditions comparable on identical windows.

**Subset playbooks? No — classify all 182.** The empty-window playbooks (77/182) are effectively free, and the malicious LOLBin windows are the scientifically interesting ones. Subsetting would bias the recall/F2 estimate. Keep the full 182/run.

**Blocker (none hard) / honesty flag**: the **EID1 LOLBin telemetry gap** caps achievable recall regardless of condition — the dissertation should frame C1-full's gain over C2/C3 as *contextual reasoning + cross-host correlation* under signal-starvation, not raw recall. And the **C2-naive "LLM baseline" claim is unsupported by the archive (tok=0)** — orchestrator must choose to either re-run C2 as a true bare-prompt LLM pass or re-label it a heuristic ablation.

---

## Reusable artifacts created
- `/home/user/mashunt-lab/scripts/eval/c1_full_classify.py` — C1-full classifier (superset of c2_naive_helper). Subcommand `classify --windows <windows.jsonl> --verdicts <analyst_verdicts.jsonl> --backend manifest --output predictions.jsonl` materializes analyst verdicts into the score-ready schema (zero SDK cost; tokens from agent quota). Also `--backend baseline-heuristic` for a deterministic lower bound (mirrors May's heuristic). Output feeds `c2_naive_helper.py score` unchanged.
- Smoke evidence: `/home/user/mashunt-lab/results/c1-full-smoke/20260527T215714Z-ba30c6/`.
