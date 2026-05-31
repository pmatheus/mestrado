# MAS-Hunt — Execution Plan (from Board briefing + research wave)

## Resolved facts
- Ground truth = **per-playbook** (185 rows/run). No per-event labels. → **Harness B (per-playbook) only.** All four conditions comparable per-playbook on the same runs (no granularity mismatch).
- `scripts/eval/c2_naive_helper.py`: `prepare` (ES Sysmon → windows.jsonl per playbook window) + `score` (predictions vs ground_truth → metrics.json: TP/FP/FN/P/R/F2 + per-lolbin). C3-elastic predictions already carry per-playbook window fields.
- C1-full / C1-nohardening / C2-naive are all LLM conditions differing only in the classifier prompt (M1-M5+M3 governance / governance-disabled / bare). C3-Elastic is non-LLM (SIEM rules) — DONE + reproduced.
- ASR/NASR live in `bootstrap_ci.py`. Adversarial manifests record injection time/place per run.
- Paper: insert `\section{Results}` at camera_raedy.tex:116 (before Conclusion); compile `latexmk -pdf -bibtex camera_raedy.tex`; reuse prose from draft_hunting_flags_v3.tex.

## Open decision (probe answers it)
- How were May C2-naive / C1-nohardening predictions generated — real LLM pass or heuristic? (May C2 SUMMARY shows tok_in=tok_out=0.) This decides total LLM cost.
- Measured per-window token cost + wall-time of one C1-full classification → sets K (runs) and whether C2/C1-nohard re-runs fit.

## TASK GRAPH

### TASK P0 — COST PROBE (go/no-go gate, BLOCKS all execution)  [general-purpose, on lab]
Build the minimal C1-full classifier as a superset of c2_naive_helper: prepare windows for ONE run, classify a 10-playbook subset via an LLM pass applying M1-M5+M3 from telemetry, emit predictions in c2_naive_helper schema, run `score` → valid metrics.json. Determine how May C2/C1-nohard predictions were produced. Measure tokens + wall-time per window. Output: measured cost + a working `c1_full_classify` path + recommended K. ACCEPTANCE: a valid metrics.json on the 10-playbook smoke + a cost number.

### TASK E1 — C1-full runs  [depends P0]  critical path
Run C1-full on the chosen subset (default 3 runs: control none/mixed + 1 mid + 1 hard adversarial tier). Commit predictions.jsonl + metrics.json per run under results/c1-full/<run_id>/.

### TASK E2 — C2-naive re-score on SAME runs  [depends P0]
Same subset/window/scorer as E1, bare prompt (or heuristic if that's how May did it — probe decides). results/c2-naive-new/<run_id>/.

### TASK E3 — C1-nohardening re-score on SAME runs  [depends P0]
Same subset, governance-disabled ablation prompt. results/c1-nohardening-new/<run_id>/.

### TASK A1 — Aggregate + bootstrap CIs + resilience contrast  [depends E1,E2,E3; C3 done]
Build single source-of-truth results JSON: per-condition per-run + aggregate P/R/F2(/FPR) with 95% bootstrap CI (B=10000). Compute the resilience metric (ASR / FP-under-contamination) showing C1-full stable vs C2-naive degrading under per-attack-burst/interleaved × encoded/steganographic. Reproducibility note: C3 already REPRODUCIBLE vs May.

### PARALLEL (no dependency on numbers) — paper drafting, can start NOW
- TASK W1 — Methods/Experimental-Setup section (lab topology, 185 playbooks, 4 injection modes × 3 tiers, 4 conditions, instrumentation) — reuse draft_hunting_flags_v3 setup prose.
- TASK W2 — Reproducibility subsection (C3 bootstrap verdict already done) + metric definitions (P/R/F2/FPR/ASR formulas from draft_hunting_flags_v3:228-241).
- TASK W3 — reference-check the bib (references.bib) for hallucinated/broken entries.

### AFTER A1 — results-dependent writing
- TASK W4 — Results section: tables (per-condition matrix + resilience contrast) populated from the source-of-truth JSON, past tense.
- TASK W5 — Discussion section (reuse draft_hunting_flags_v3:243-269 structure) grounded in the numbers.
- TASK W6 — convert Validation Plan → executed; fix abstract tense; compile `latexmk -pdf -bibtex`; verify zero errors / no undefined refs.

## Validation (Round-2, fresh memory)
- LaTeX compile-clean (no errors, no undefined \ref/\cite).
- Number-consistency: every table cell == source-of-truth results JSON.
- No-fabrication / no-future-tense audit on Results.
- Cross-validate metrics: independent recompute of one condition.
