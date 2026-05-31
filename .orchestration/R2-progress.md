# R2 — Classification on v2 windows (progress ledger)

Dataset: 10 health-gated v2 runs (telemetry validated, ws02 shipping). Windows in `results/_matrix-windows-v2/<run>/`. Batches `results/c1-full-orch-v2/<run>/batches5/{G1..G5}.json`. Prompts: `results/c1-full-orchestrated/HUNTER_C1FULL_PROMPT.md` + `HUNTER_C1NOHARD_PROMPT.md`. Score via `c2_naive_helper.py score --run-dir results/attack-v2/<run> ...`.

## Runs (run_id : mode/tier)
1. 20260529T192442Z-b1ab0d : none/mixed (control)
2. 20260529T202123Z-384471 : pre-burst/overt
3. 20260529T211933Z-3df1a1 : pre-burst/encoded
4. 20260529T221735Z-492768 : pre-burst/steganographic
5. 20260529T231559Z-02fc9c : per-attack-burst/overt
6. 20260530T005129Z-53a2cb : per-attack-burst/encoded
7. 20260530T022438Z-19f80c : per-attack-burst/steganographic
8. 20260530T040359Z-eedb0f : interleaved/overt
9. 20260530T053439Z-702a1a : interleaved/encoded
10. 20260530T070504Z-96829d : interleaved/steganographic

## Conditions
- C1-full (real orchestration, 5 hunters/run, M1-M5+M3) → results/c1full-orch-v2/<run>/  [MAIN-AGENT WAVES, ≤5]
- C1-nohardening (real orchestration, 5 hunters/run, M3-only) → results/c1nohard-orch-v2/<run>/  [WAVES]
- C2-naive (single-pass, automated script claude -p bare) → results/c2-naive-v2/<run>/  [AUTOMATED, matrix manager]
- C3-Elastic (SIEM rules, automated) → results/c3-elastic-v2/<run>/  [AUTOMATED, matrix manager]

## Status ledger (update each wave: run# cond = F2 or PENDING)
C1-full:    1- 2- 3- 4- 5- 6- 7- 8- 9- 10-   (all PENDING)
C1-nohard:  1- 2- 3- 4- 5- 6- 7- 8- 9- 10-   (all PENDING)
C2-naive:   AUTOMATED (dispatched to matrix manager)
C3-Elastic: AUTOMATED (dispatched to matrix manager)

## After all cells: R3
Aggregate → bootstrap CIs (per-condition, per-tier) → fill Results/Discussão/Conclusão in mashunt/camera_raedy.tex + dissertacao/cap6,7,8 → compile both PDFs.
