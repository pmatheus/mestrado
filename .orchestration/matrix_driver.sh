#!/usr/bin/env bash
# MAS-Hunt LLM detection matrix driver — 3 conditions x 3 runs, real LLM pass.
# Detached job: prepares windows once per run, then classifies each window with
# the authenticated `claude -p` CLI under three governance system prompts,
# scores each against the same per-playbook ground truth.
#
# Conditions: c2-naive (bare), c1-nohardening (M3, M1-M5 off), c1-full (M3+M1-M5).
# Backend: api (claude CLI / OAuth quota). Predictions keyed by window_id.

set -uo pipefail

LAB_BASE=/home/user/mashunt-lab
cd "$LAB_BASE" || exit 1

TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$LAB_BASE/results/matrix-run-${TS}.log"
EVAL=scripts/eval
PY=python3
CONC="${CONC:-10}"

RUNS=(
  "20260527T215714Z-ba30c6"   # control: none/mixed
  "20260528T044122Z-225fc6"   # hard adversarial: per-attack-burst/steganographic
  "20260528T091131Z-6bd91b"   # hard adversarial: interleaved/steganographic
)

# condition -> output dir prefix
declare -A OUTDIR=(
  ["c1-full"]="results/c1-full-new"
  ["c1-nohardening"]="results/c1-nohardening-new"
  ["c2-naive"]="results/c2-naive-new"
)
CONDITIONS=("c1-full" "c1-nohardening" "c2-naive")

log() { echo "[$(date -u +%H:%M:%S)] $*" | tee -a "$LOG"; }

log "=== MATRIX RUN ${TS} START === conc=${CONC}"
log "runs: ${RUNS[*]}"
log "conditions: ${CONDITIONS[*]}"

for RUN in "${RUNS[@]}"; do
  RUNDIR="results/attack/${RUN}"
  # Shared windows.jsonl per run (prepared ONCE, used by all 3 conditions).
  WINDIR="results/_matrix-windows/${RUN}"
  mkdir -p "$WINDIR"
  WIN="$WINDIR/windows.jsonl"
  GT="$WINDIR/ground_truth.jsonl"

  if [[ -s "$WIN" && -s "$GT" ]]; then
    log "[$RUN] windows.jsonl already present ($(wc -l < "$WIN") rows) — reuse"
  else
    log "[$RUN] prepare windows.jsonl ..."
    $PY $EVAL/c2_naive_helper.py prepare \
      --run-dir "$RUNDIR" \
      --output "$WIN" >>"$LOG" 2>&1
    # prepare writes ground_truth.jsonl next to --output
    if [[ ! -s "$GT" ]]; then
      log "[$RUN] ERROR: ground_truth.jsonl not produced by prepare"
    fi
    log "[$RUN] prepared $(wc -l < "$WIN" 2>/dev/null || echo 0) windows"
  fi

  for COND in "${CONDITIONS[@]}"; do
    OD="${OUTDIR[$COND]}/${RUN}"
    mkdir -p "$OD"
    cp -f "$GT" "$OD/ground_truth.jsonl"
    log "[$RUN/$COND] classify (backend=api) ..."
    $PY $EVAL/c1_full_classify.py classify \
      --windows "$WIN" \
      --backend api \
      --condition "$COND" \
      --concurrency "$CONC" \
      --max-retries 4 \
      --usage-log "$OD/usage.jsonl" \
      --output "$OD/predictions.jsonl" >>"$LOG" 2>&1
    log "[$RUN/$COND] classify done; scoring ..."
    $PY $EVAL/c2_naive_helper.py score \
      --run-dir "$RUNDIR" \
      --predictions "$OD/predictions.jsonl" \
      --output-dir "$OD" >>"$LOG" 2>&1
    if [[ -s "$OD/metrics.json" ]]; then
      M=$($PY -c "import json;d=json.load(open('$OD/metrics.json'));print('TP=%d FP=%d FN=%d TN=%d P=%.3f R=%.3f F2=%.3f'%(d['tp'],d['fp'],d['fn'],d['tn'],d['precision'],d['recall'],d['f2']))" 2>/dev/null)
      log "[$RUN/$COND] METRICS: $M -> $OD/metrics.json"
    else
      log "[$RUN/$COND] ERROR: no metrics.json produced"
    fi
  done
done

log "=== MATRIX RUN ${TS} COMPLETE ==="
log "output dirs: results/{c1-full-new,c1-nohardening-new,c2-naive-new}/<run_id>/{predictions,metrics,fpr,usage}.{json,jsonl}"
