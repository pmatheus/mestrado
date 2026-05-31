#!/usr/bin/env bash
# C2-naive single-pass baseline on the PRISTINE v2 windows — 10 runs.
# Bare prompt, NO governance (c1_full_classify.py --backend api --condition
# c2-naive). Reuses the already-prepared v2 windows; no re-prepare.
#
# Robust config (proven on the 6bd91b re-run and overt/encoded matrix):
#   concurrency 3, max-retries 5 + exponential backoff, MAX_ERR=0 assert gate.
# A cell with errors>0 is NOT scored/committed-as-clean — its stale metrics.json
# is removed (reads as incomplete), contaminated predictions left for
# inspection, and the driver CONTINUES (credit exhaustion on one run does not
# block the rest → resume only the run_ids missing metrics.json).
#
# *** PREP ONLY — DO NOT auto-run. Trigger manually after the
#     C1-full / C1-nohardening orchestration waves finish (credit control). ***
#
# Per run: copy ground_truth into the c2 dir, classify (api, c2-naive), assert
# errors==0, score against the v2 attack run dir, write usage.json.

set -uo pipefail

LAB_BASE=/home/user/mashunt-lab
cd "$LAB_BASE" || exit 1

EVAL=scripts/eval
PY=python3
COND="c2-naive"
ATTACK_ROOT="results/attack-v2"
WIN_ROOT="results/_matrix-windows-v2"
OUT_ROOT="results/c2-naive-v2"
CONC="${CONC:-3}"
RETRIES="${RETRIES:-5}"
MAX_ERR="${MAX_ERR:-0}"

TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$LAB_BASE/results/c2-naive-v2-${TS}.log"

if [[ -n "${RUNS_OVERRIDE:-}" ]]; then
  # Space-separated run_ids to scope the sweep (e.g. signal-rich subset only).
  read -r -a RUNS <<< "$RUNS_OVERRIDE"
else
  RUNS=(
    "20260529T192442Z-b1ab0d"   # none/mixed
    "20260529T202123Z-384471"   # pre-burst/overt
    "20260529T211933Z-3df1a1"   # pre-burst/encoded
    "20260529T221735Z-492768"   # pre-burst/steg
    "20260529T231559Z-02fc9c"   # per-attack-burst/overt
    "20260530T005129Z-53a2cb"   # per-attack-burst/encoded
    "20260530T022438Z-19f80c"   # per-attack-burst/steg
    "20260530T040359Z-eedb0f"   # interleaved/overt
    "20260530T053439Z-702a1a"   # interleaved/encoded
    "20260530T070504Z-96829d"   # interleaved/steg
  )
fi

log() { echo "[$(date -u +%H:%M:%S)] $*" | tee -a "$LOG"; }

log "=== C2-NAIVE v2 ${TS} START === conc=${CONC} retries=${RETRIES} max_err=${MAX_ERR} runs=${#RUNS[@]}"
log "run_ids: ${RUNS[*]}"

CLEAN=0
FAILED=0

for RUN in "${RUNS[@]}"; do
  RUNDIR="${ATTACK_ROOT}/${RUN}"
  WIN="${WIN_ROOT}/${RUN}/windows.jsonl"
  GT="${WIN_ROOT}/${RUN}/ground_truth.jsonl"
  OD="${OUT_ROOT}/${RUN}"

  if [[ ! -s "$WIN" || ! -s "$GT" ]]; then
    log "[$RUN] ERROR: v2 windows/ground_truth missing ($WIN) — preparing"
    mkdir -p "${WIN_ROOT}/${RUN}"
    $PY $EVAL/c2_naive_helper.py prepare --run-dir "$RUNDIR" --output "$WIN" >>"$LOG" 2>&1
  fi

  mkdir -p "$OD"
  cp -f "$GT" "$OD/ground_truth.jsonl"

  log "[$RUN/$COND] classify (api, conc=${CONC}, retries=${RETRIES}) ..."
  $PY $EVAL/c1_full_classify.py classify \
    --windows "$WIN" \
    --backend api \
    --condition "$COND" \
    --concurrency "$CONC" \
    --max-retries "$RETRIES" \
    --usage-log "$OD/usage.jsonl" \
    --output "$OD/predictions.jsonl" >>"$LOG" 2>&1

  NERR=$($PY -c "import json;print(sum(1 for l in open('$OD/predictions.jsonl') if l.strip() and json.loads(l).get('reasoning','').startswith('ERROR')))" 2>/dev/null || echo 999)
  NWIN=$($PY -c "print(sum(1 for l in open('$OD/predictions.jsonl') if l.strip()))" 2>/dev/null || echo 0)
  NMAL=$($PY -c "import json;print(sum(1 for l in open('$OD/predictions.jsonl') if l.strip() and json.loads(l).get('predicted_malicious')))" 2>/dev/null || echo 0)

  $PY - "$OD" "$NWIN" "$NERR" "$NMAL" <<'PYEOF' >>"$LOG" 2>&1
import json, sys, pathlib
od, nwin, nerr, nmal = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
tin=tout=cr=cc=0; cost=0.0; rows=0
up = pathlib.Path(od) / "usage.jsonl"
if up.exists():
    for line in up.open():
        if not line.strip(): continue
        u=json.loads(line); rows+=1
        tin+=u.get("input_tokens",0); tout+=u.get("output_tokens",0)
        cr+=u.get("cache_read_input_tokens",0); cc+=u.get("cache_creation_input_tokens",0)
        cost+=u.get("cost_usd",0.0)
summary={"windows":nwin,"errors":nerr,"malicious":nmal,"usage_rows":rows,
         "tok_in":tin,"tok_out":tout,"cache_read":cr,"cache_create":cc,"cost_usd":round(cost,4)}
(pathlib.Path(od)/"usage.json").write_text(json.dumps(summary,indent=2)+"\n")
print("usage.json:", json.dumps(summary))
PYEOF

  if [[ "$NERR" -gt "$MAX_ERR" ]]; then
    FAILED=$((FAILED+1))
    log "[$RUN/$COND] FAILED: errors=$NERR > max_err=$MAX_ERR — NOT scoring; removing stale metrics (cell reads as incomplete)"
    rm -f "$OD/metrics.json" "$OD/fpr.json"
    log "[$RUN/$COND] RESUME-NEEDED (predictions left at $OD/predictions.jsonl)"
    continue
  fi

  log "[$RUN/$COND] clean: windows=$NWIN errors=$NERR malicious=$NMAL ; scoring ..."
  $PY $EVAL/c2_naive_helper.py score \
    --run-dir "$RUNDIR" \
    --predictions "$OD/predictions.jsonl" \
    --output-dir "$OD" >>"$LOG" 2>&1
  if [[ -s "$OD/metrics.json" ]]; then
    M=$($PY -c "import json;d=json.load(open('$OD/metrics.json'));print('TP=%d FP=%d FN=%d TN=%d P=%.3f R=%.3f F2=%.3f'%(d['tp'],d['fp'],d['fn'],d['tn'],d['precision'],d['recall'],d['f2']))" 2>/dev/null)
    CLEAN=$((CLEAN+1))
    log "[$RUN/$COND] METRICS: $M -> $OD/metrics.json  (clean so far: $CLEAN)"
  else
    FAILED=$((FAILED+1))
    log "[$RUN/$COND] ERROR: no metrics.json produced despite errors==0"
  fi
done

log "=== C2-NAIVE v2 ${TS} COMPLETE === clean=$CLEAN failed=$FAILED (target=10)"
