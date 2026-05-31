# MAS-Hunt — Board Situation Brief (2026-05-28)

## Mission
Master's dissertation: **MAS-Hunt — a resilient multi-agent AI system for threat hunting / spyware detection in Windows**, integrated with Elastic Security. Two deliverables (in priority order): (1) finish + compile the IEEE/MDPI paper `camera_raedy.tex`; (2) later, the full ABNT dissertation.

## What just happened (verified facts)
- The lab was brought back up: Win Server 2025 DC (`mashunt-dc01`) + 2 Win11 (`ws01`, `ws02`) joined to the lab AD domain, fully instrumented (Sysmon + Elastic Agent + audit policies). Elastic 9.3.4 healthy, 6 Fleet agents.
- A **clean full re-run** of the experiment completed: control (none/mixed) + 9 adversarial conditions (3 injection modes × 3 sophistication tiers), 185 LOLBin playbooks each, 3 VMs. Artifacts in `mashunt-lab/results/attack/<run_id>/` (10 new runs, 2026-05-27/28). May runs archived to `results/_archive-2026-05/`.
- **C3-Elastic baseline** (SIEM default rules) was re-scored on the 10 new runs and a formal **reproducibility verdict** was produced via bootstrap CI (B=10000, 95%): Precision/Recall/F2 all REPRODUCIBLE vs May (each point estimate inside the other's CI). Saved at `results/reproducibility/VERDICT.json`.

## The data gap (why we're orchestrating)
The experiment compares detection **conditions**:
- **C3-Elastic** = Elastic SIEM default rules. ✅ Done + reproduced.
- **C2-naive** = single-pass LLM, no governance. May archive has results; NOT re-scored on new runs.
- **C1-nohardening** = MAS-Hunt with governance mechanisms disabled (ablation). May archive has per-run metrics; NOT re-scored on new runs.
- **C1-full** = the PROPOSED MAS-Hunt system (full M1-M5 governance + M3 analysis framework). **NO results exist anywhere.** This is the dissertation's central contribution and the paper's headline claim.

User decision: **run C1-full now** (+ re-score C1-nohardening and C2-naive on the new runs) to produce the full comparison matrix, then write the paper.

## Execution harnesses (to be mapped precisely by Managers)
- **Harness A** — `/hunt-experiment` skill: a 5-team Claude-Code orchestration that classifies per-event ground-truth (`experiment/corpus/ground-truth/labels.jsonl`) by querying `logs-windows.sysmon_operational-default`. Conditions C1-full (M1-M5 + M3 OBSERVE→HYPOTHESIZE→EVIDENCE→CROSS-VALIDATE→CLASSIFY) vs C2-naive (bare). Output: `experiment/results/raw/{CONDITION}/run_{idx}/`. LLM-costly.
- **Harness B** — `lab-attack-orchestrator.py` + `eval/c3_baseline_v2.py`: per-playbook detection windows vs `.alerts-security.alerts-default`; produced the 10 attack runs + C3 scoring. Eval helpers: `compute_metrics.py`, `compute_fpr.py`, `c2_naive_helper.py` (prepare/score, NO live LLM), `bootstrap_ci.py`.
- Open question for Managers' research agents: how C1-full/C1-nohardening/C2 map onto the new attack runs, whether ground-truth labels exist for the new runs, and the LLM cost/time of C1-full (likely scope to 1 run/condition or a subset, not all 10).

## Paper state (`/Users/user/mestrado/mashunt/camera_raedy.tex`, MDPI engproc)
- Complete: Intro, Lit Review, Architecture (3-layer governance), Testable Hypothesis.
- MISSING: a real **Results** section (currently only a future-tense "Validation Plan"), **Discussion**, results tables, reproducibility subsection. Bib: `references.bib`. No PDF compiled yet.
- "Finish" = convert Validation Plan → executed Results+Discussion with the C1/C2/C3 matrix + adversarial-resilience story + reproducibility, past tense, tables/figures, compile to PDF.

## Access
- Lab: `ssh -o BindAddress=0.0.0.0 lab-ts '<cmd>'` (Tailscale; the plain `lab` LAN alias is dead off-LAN). ES via in-container creds: `docker exec mashunt-es bash -c 'curl -sk -u elastic:$ELASTIC_PASSWORD <url>'`. Secrets hook blocks Bash containing the literal env-file token or bare word `env`.
- Paper files are local under `/Users/user/mestrado`.

## Hard constraints
- **Research integrity**: NEVER fabricate experimental numbers. Results must come from actual runs/scoring. If a condition can't be run, the paper must scope it honestly as future work.
- Quality > speed. Reproducibility is the dissertation's theme — everything must be re-runnable.
