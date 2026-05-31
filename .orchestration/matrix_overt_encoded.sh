#!/usr/bin/env bash
# MAS-Hunt LLM detection matrix — OVERT + ENCODED adversarial tiers.
# 6 runs x 3 conditions = 18 cells. Robust config (proven on the 6bd91b re-run):
#   concurrency 3, max-retries 5 + exponential backoff, MAX_ERR=0 assert gate.
# A cell with errors>0 is NOT scored/committed-as-clean — it is recorded as
# FAILED and the driver moves on (so credit exhaustion on one cell does not
# block the rest; unfinished cells can be resumed later).
#
# Per run: prepare windows.jsonl ONCE (reuse if present) -> for each condition
# copy ground_truth, classify (api), assert errors==0, score, write usage.json.

set -uo pipefail

LAB_BASE=/home/user/mashunt-lab
cd "$LAB_BASE" || exit 1

EVAL=scripts/eval
PY=python3
CONC="${CONC:-3}"
RETRIES="${RETRIES:-5}"
MAX_ERR="${MAX_ERR:-0}"

TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$LAB_BASE/results/matrix-overt-encoded-${TS}.log"

RUNS=(
  "20260527T224956Z-a253dd"   # pre-burst/overt
  "20260527T234443Z-bb41ce"   # pre-burst/encoded
  "20260528T013438Z-0fa87b"   # per-attack-burst/overt
  "20260528T030824Z-d5174f"   # per-attack-burst/encoded
  "20260528T061558Z-3d51f1"   # interleaved/overt
  "20260528T074305Z-5b2b20"   # interleaved/encoded
)

declare -A OUTDIR=(
  ["c1-full"]="results/c1-full-new"
  ["c1-nohardening"]="results/c1-nohardening-new"
  ["c2-naive"]="results/c2-naive-new"
)
CONDITIONS=("c1-full" "c1-nohardening" "c2-naive")

log() { echo "[$(date -u +%H:%M:%S)] $*" | tee -a "$LOG"; }

log "=== OVERT/ENCODED MATRIX ${TS} START === conc=${CONC} retries=${RETRIES} max_err=${MAX_ERR}"
log "runs: ${RUNS[*]}"

CLEAN=0
FAILED=0

for RUN in "${RUNS[@]}"; do
  RUNDIR="results/attack/${RUN}"
  WINDIR="results/_matrix-windows/${RUN}"
  mkdir -p "$WINDIR"
  WIN="$WINDIR/windows.jsonl"
  GT="$WINDIR/ground_truth.jsonl"

  if [[ -s "$WIN" && -s "$GT" ]]; then
    log "[$RUN] windows present ($(wc -l < "$WIN") rows) — reuse"
  else
    log "[$RUN] prepare windows.jsonl ..."
    $PY $EVAL/c2_naive_helper.py prepare --run-dir "$RUNDIR" --output "$WIN" >>"$LOG" 2>&1
    log "[$RUN] prepared $(wc -l < "$WIN" 2>/dev/null || echo 0) windows, gt=$(wc -l < "$GT" 2>/dev/null || echo 0)"
  fi

  for COND in "${CONDITIONS[@]}"; do
    OD="${OUTDIR[$COND]}/${RUN}"
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
      log "[$RUN/$COND] FAILED: errors=$NERR > max_err=$MAX_ERR — NOT scoring; removing stale metrics so cell reads as incomplete"
      rm -f "$OD/metrics.json" "$OD/fpr.json"
      log "[$RUN/$COND] RESUME-NEEDED (contaminated predictions left for inspection at $OD/predictions.jsonl)"
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
      log "[$RUN/$COND] METRICS: $M -> $OD/metrics.json  (clean cells so far: $CLEAN)"
    else
      FAILED=$((FAILED+1))
      log "[$RUN/$COND] ERROR: no metrics.json produced despite errors==0"
    fi
  done
done

log "=== OVERT/ENCODED MATRIX ${TS} COMPLETE === clean_cells=$CLEAN failed_cells=$FAILED (target=18)"
