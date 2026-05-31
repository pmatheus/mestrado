#!/usr/bin/env bash
# Health-gated v2 sweep with STAGGERED BOOTS (crash-hardened).
#
# ROOT CAUSE of the prior box crash: booting dc01+ws01+ws02 simultaneously spiked
# CPU load to ~110 and RAM beyond headroom; the box OOM-died. Steady-state 3 VMs
# (~30GB/62GB) is fine. So this sweep NEVER boots VMs simultaneously.
#
# Per condition:
#   1) stop all + restore disks (lab-snapshot.py restore-no-start; NO auto-start)
#   2) STAGGERED boot, one VM at a time, gated:
#        start dc01 -> gate dc01 (EID1 + WinRM) -> start ws01 -> gate ws01 ->
#        start ws02 -> gate ws02
#      Each VM fully boots and its agent checks in BEFORE the next one starts.
#   3) only after all 3 individually healthy: execute orchestrator
#   4) extract windows v2
#
# Output: results/attack-v2/<run_id>/ (MASHUNT_RESULTS_ROOT). Never clobbers
# results/attack. Resume with START_CONDITION (1-indexed into CONDITIONS).
#
# Faithful params: profile=full, vms=dc01,ws01,ws02, burst 5, interleave 1,
# pre-burst 200 (adversarial), 185 playbooks.
#
# Launch detached:
#   setsid nohup bash lab-run-sweep-v2-gated.sh > <log> 2>&1 < /dev/null &

set -uo pipefail

LAB_HOME="${HOME}/mashunt-lab"
SCRIPTS="${LAB_HOME}/scripts"
export MASHUNT_RESULTS_ROOT="${LAB_HOME}/results/attack-v2"
LOG_DIR="${MASHUNT_RESULTS_ROOT}"
mkdir -p "$LOG_DIR"
SWEEP_LOG="${LOG_DIR}/sweep-v2-$(date -u +%Y%m%dT%H%M%SZ).log"

GATE_TIMEOUT_SEC="${GATE_TIMEOUT_SEC:-1200}"   # per-host gate timeout
MIN_FRESH_EID1="${MIN_FRESH_EID1:-5}"
BOOT_SETTLE_SEC="${BOOT_SETTLE_SEC:-60}"       # let a single VM's QEMU spin up
VMS="${VMS:-dc01,ws01,ws02}"
PROFILE="${PROFILE:-full}"
PRE_BURST="${PRE_BURST:-200}"
MAX_PLAYBOOKS="${MAX_PLAYBOOKS:-0}"            # 0 = all 185
START_CONDITION="${START_CONDITION:-1}"

exec > >(tee -a "$SWEEP_LOG") 2>&1

# Condition list: control first, then 3 modes x 3 tiers.
CONDITIONS=(
  "none|mixed"
  "pre-burst|overt"
  "pre-burst|encoded"
  "pre-burst|steganographic"
  "per-attack-burst|overt"
  "per-attack-burst|encoded"
  "per-attack-burst|steganographic"
  "interleaved|overt"
  "interleaved|encoded"
  "interleaved|steganographic"
)

# host short -> ES host.name for per-host gating
declare -A ESNAME=( [dc01]=dc01-server [ws01]=ws01-client [ws02]=ws02-client )

echo "=== v2 STAGGERED health-gated sweep starting $(date -Iseconds) ==="
echo "results_root=${MASHUNT_RESULTS_ROOT}"
echo "conditions=${#CONDITIONS[@]}  start=${START_CONDITION}"
echo "gate_timeout=${GATE_TIMEOUT_SEC}s min_fresh_eid1=${MIN_FRESH_EID1} boot_settle=${BOOT_SETTLE_SEC}s"
echo "vms=${VMS} profile=${PROFILE} pre_burst=${PRE_BURST} max_playbooks=${MAX_PLAYBOOKS}"
echo "log=${SWEEP_LOG}"

# Boot ONE VM container and gate ONLY that host until EID1+WinRM healthy.
# Retries the boot if its QEMU crashes (ws02 monitor assertion).
boot_and_gate_one() {
  local vm="$1"
  local container="mashunt-${vm}"
  local esname="${ESNAME[$vm]}"
  echo "  -- staggered boot: ${vm} (${esname}) --"
  for attempt in 1 2 3; do
    local st
    st=$(docker inspect -f '{{.State.Status}}' "$container" 2>/dev/null || echo missing)
    if [[ "$st" != "running" ]]; then
      docker start "$container" >/dev/null 2>&1 || true
    fi
    echo "     [${vm}] settle ${BOOT_SETTLE_SEC}s for QEMU boot (attempt ${attempt})"
    sleep "$BOOT_SETTLE_SEC"
    if uv run "$SCRIPTS/eval/telemetry_health_gate.py" \
          --hosts "$esname" \
          --timeout-sec "$GATE_TIMEOUT_SEC" \
          --min-fresh-eid1 "$MIN_FRESH_EID1"; then
      echo "     [${vm}] HEALTHY"
      return 0
    fi
    echo "     [${vm}] gate attempt ${attempt} failed; status=$(docker inspect -f '{{.State.Status}}' "$container" 2>/dev/null); retrying"
    docker start "$container" >/dev/null 2>&1 || true
  done
  echo "     [${vm}] NOT healthy after retries — FLAGGED (verification will catch it)"
  return 1
}

cidx=0
for cond in "${CONDITIONS[@]}"; do
  cidx=$((cidx + 1))
  mode="${cond%%|*}"
  tier="${cond##*|}"
  label="${cidx}/${#CONDITIONS[@]} mode=${mode} tier=${tier}"
  if (( cidx < START_CONDITION )); then
    echo "  [skip] condition ${label} (START_CONDITION=${START_CONDITION})"
    continue
  fi

  echo
  echo "============================================================"
  echo "  condition ${label}  $(date -Iseconds)"
  echo "============================================================"

  echo "-- stop all + restore disks (NO auto-start) --"
  cd "$LAB_HOME"
  uv run "$SCRIPTS/lab-snapshot.py" restore-no-start || {
    echo "ERROR: restore-no-start failed for ${label}; skipping condition"
    continue
  }

  echo "-- STAGGERED boot + per-host gate (dc01 -> ws01 -> ws02) --"
  boot_and_gate_one dc01 || true
  boot_and_gate_one ws01 || true
  boot_and_gate_one ws02 || true

  echo "-- all VMs individually gated; executing orchestrator (mode=${mode} tier=${tier}) --"
  cd "$LAB_HOME"
  if [[ "$mode" == "none" ]]; then
    uv run "$SCRIPTS/lab-attack-orchestrator.py" \
      --mode "$mode" --tier "$tier" --vms "$VMS" --profile "$PROFILE" \
      --max-playbooks "$MAX_PLAYBOOKS" || echo "ERROR: orchestrator failed for ${label}; continuing"
  else
    uv run "$SCRIPTS/lab-attack-orchestrator.py" \
      --mode "$mode" --tier "$tier" --vms "$VMS" --profile "$PROFILE" \
      --burst-size 5 --interleave-count 1 --pre-burst-size "$PRE_BURST" \
      --max-playbooks "$MAX_PLAYBOOKS" || echo "ERROR: orchestrator failed for ${label}; continuing"
  fi

  # Identify the run_id just produced (newest dir) and extract windows v2.
  RUN_DIR=$(ls -td "${MASHUNT_RESULTS_ROOT}"/2026*/ 2>/dev/null | head -1)
  if [[ -n "$RUN_DIR" && -f "${RUN_DIR}summary.json" ]]; then
    RID=$(basename "$RUN_DIR")
    echo "-- extracting windows v2 for ${RID} --"
    OUT="${LAB_HOME}/results/_matrix-windows-v2/${RID}"
    mkdir -p "$OUT"
    uv run "$SCRIPTS/eval/c2_naive_helper.py" prepare-v2 \
      --run-dir "${RUN_DIR%/}" --output "${OUT}/windows.jsonl" \
      || echo "WARN: prepare-v2 failed for ${RID}"
  fi
  echo "-- condition ${label} done $(date -Iseconds) --"
done

echo
echo "=== v2 STAGGERED sweep finished $(date -Iseconds) ==="
echo "Per-condition artifacts: ${MASHUNT_RESULTS_ROOT}/<run_id>/"
echo "Windows v2: ${LAB_HOME}/results/_matrix-windows-v2/<run_id>/"
echo "Sweep log: ${SWEEP_LOG}"
