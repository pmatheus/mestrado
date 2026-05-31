#!/usr/bin/env bash
# Robust re-run of the 3 failed cells on run 6bd91b (interleaved/steganographic).
# Event-heavy run that exhausted credits/rate-limits on the first matrix pass.
# Lower concurrency + more retries; assert errors==0 per cell before scoring;
# write an auditable usage.json summary per cell. Reuses the existing
# windows.jsonl (already prepared). Overwrites only the 6bd91b cells.

set -uo pipefail

LAB_BASE=/home/user/mashunt-lab
cd "$LAB_BASE" || exit 1

RUN="20260528T091131Z-6bd91b"
RUNDIR="results/attack/${RUN}"
WIN="results/_matrix-windows/${RUN}/windows.jsonl"
GT="results/_matrix-windows/${RUN}/ground_truth.jsonl"

EVAL=scripts/eval
PY=python3
CONC="${CONC:-3}"
RETRIES="${RETRIES:-5}"
MAX_ERR="${MAX_ERR:-0}"          # max tolerated ERROR windows before STOP

TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$LAB_BASE/results/rerun-6bd91b-${TS}.log"

declare -A OUTDIR=(
  ["c1-full"]="results/c1-full-new"
  ["c1-nohardening"]="results/c1-nohardening-new"
  ["c2-naive"]="results/c2-naive-new"
)
CONDITIONS=("c1-full" "c1-nohardening" "c2-naive")

log() { echo "[$(date -u +%H:%M:%S)] $*" | tee -a "$LOG"; }

log "=== RERUN 6bd91b ${TS} START === conc=${CONC} retries=${RETRIES} max_err=${MAX_ERR}"

if [[ ! -s "$WIN" || ! -s "$GT" ]]; then
  log "ERROR: windows.jsonl/ground_truth.jsonl missing for ${RUN} — preparing"
  mkdir -p "results/_matrix-windows/${RUN}"
  $PY $EVAL/c2_naive_helper.py prepare --run-dir "$RUNDIR" --output "$WIN" >>"$LOG" 2>&1
fi
log "windows=$(wc -l < "$WIN") ground_truth=$(wc -l < "$GT")"

for COND in "${CONDITIONS[@]}"; do
  OD="${OUTDIR[$COND]}/${RUN}"
  mkdir -p "$OD"
  cp -f "$GT" "$OD/ground_truth.jsonl"

  log "[$COND] classify (api, conc=${CONC}, retries=${RETRIES}) ..."
  $PY $EVAL/c1_full_classify.py classify \
    --windows "$WIN" \
    --backend api \
    --condition "$COND" \
    --concurrency "$CONC" \
    --max-retries "$RETRIES" \
    --usage-log "$OD/usage.jsonl" \
    --output "$OD/predictions.jsonl" >>"$LOG" 2>&1

  # Count ERROR-defaulted windows (the failure signature).
  NERR=$($PY -c "import json;print(sum(1 for l in open('$OD/predictions.jsonl') if l.strip() and json.loads(l).get('reasoning','').startswith('ERROR')))" 2>/dev/null || echo 999)
  NWIN=$($PY -c "print(sum(1 for l in open('$OD/predictions.jsonl') if l.strip()))" 2>/dev/null || echo 0)
  NMAL=$($PY -c "import json;print(sum(1 for l in open('$OD/predictions.jsonl') if l.strip() and json.loads(l).get('predicted_malicious')))" 2>/dev/null || echo 0)

  # Auditable usage.json summary from usage.jsonl.
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
    log "[$COND] STOP: errors=$NERR > max_err=$MAX_ERR — NOT scoring (contaminated cell left for inspection)"
    log "=== RERUN ABORTED at $COND ==="
    exit 2
  fi

  log "[$COND] classify clean: windows=$NWIN errors=$NERR malicious=$NMAL ; scoring ..."
  $PY $EVAL/c2_naive_helper.py score \
    --run-dir "$RUNDIR" \
    --predictions "$OD/predictions.jsonl" \
    --output-dir "$OD" >>"$LOG" 2>&1
  if [[ -s "$OD/metrics.json" ]]; then
    M=$($PY -c "import json;d=json.load(open('$OD/metrics.json'));print('TP=%d FP=%d FN=%d TN=%d P=%.3f R=%.3f F2=%.3f'%(d['tp'],d['fp'],d['fn'],d['tn'],d['precision'],d['recall'],d['f2']))" 2>/dev/null)
    log "[$COND] METRICS: $M -> $OD/metrics.json"
  else
    log "[$COND] ERROR: no metrics.json produced"
  fi
done

log "=== RERUN 6bd91b ${TS} COMPLETE (all 3 cells clean) ==="
