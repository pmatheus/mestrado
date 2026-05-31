# R1 — Telemetry Pipeline Fix + Health-Gated Pristine Re-Collection

**Phase**: R1 (cheap — orchestrator/WinRM + scripting; NO LLM classification)
**Date**: 2026-05-29
**Lab**: `/home/user/mashunt-lab` (reached via `lab-ts` Tailscale)
**Author**: Execution Manager (R1)

> **UPDATE (R1b, 2026-05-29 19:xx UTC)** — the first v2 sweep CRASHED the lab box:
> the simultaneous 3-VM boot storm spiked load to ~110 and, with only zram swap,
> OOM-killed the host. Box rebooted; ELK auto-recovered. Hardened with STAGGERED
> BOOTS (one VM at a time, gated) + lower ES heap + a real 12GB disk swap, then
> relaunched. See section 7 for the crash-hardening; sections 1-6 document the
> original fix and remain valid (the health gate and extraction are unchanged
> except the gate gained a `--hosts` flag for per-host staggered gating).

---

## 0. The bug, restated

Prior control + low-signal runs shipped BROKEN telemetry: playbooks executed right
after VM restore, before the workstation Elastic Agents / Sysmon checked in to
Fleet. Result: ws02-client shipped ZERO events, ws01-client ~1900, malicious-
playbook process-creation (Sysmon EID1) absent from ES, while dc01-server shipped
484k. The blind `sleep 240` was not a reliable readiness signal.

**Root cause confirmed during this phase**: two independent failure layers, both
now gated:
1. **Agent/Sysmon check-in lag** — after restore the agents take a variable
   amount of time to start shipping; a fixed sleep races them.
2. **ws02 QEMU instability** — `mashunt-ws02`'s QEMU intermittently hits
   `monitor/monitor.c:381: monitor_qapi_event_queue_no_reenter` assertion right
   after Windows boots, and the container exits (ExitCode=0, "Forcefully
   terminating Windows"). When it crashes, ws02 has no telemetry AND no WinRM —
   exactly the original zero-data symptom. It recovers on `docker start`.

There is also a structural caveat (NOT a bug I can fix in R1): the **EID1 LOLBin
telemetry gap** — ~87% of Sysmon docs are EID12/13 registry; on signal-starved
runs (control, pre-burst) the LOLBin process-creates are sparsely captured. The
improved extraction (Task 2) maximizes capture of whatever EID1 exists, and on
signal-rich runs recovers the full attack chain (verified below), but it cannot
manufacture process-creates Sysmon never logged.

---

## 1. Telemetry-health gate (Task 1) — `scripts/eval/telemetry_health_gate.py`

Replaces the blind `sleep 240`. Polls Elasticsearch until ALL THREE hosts
(dc01-server, ws01-client, ws02-client) are live on BOTH layers the orchestrator
depends on, then unblocks. Hard timeout 20 min (`--timeout-sec 1200`).

**A host is HEALTHY iff (per poll):**
- it has shipped `>= --min-fresh-eid1` (default 5) FRESH Sysmon EID1 process-
  creation docs since the gate started, AND
- its WinRM heartbeat returns `ok` (port 5985 reachable + PowerShell runs).

**Design decisions (and why):**

- **Clock-skew safe.** The lab Windows VM clocks run ~7h AHEAD of the lab host
  clock (observed: ws01 EID1 `@timestamp=2026-05-29T22:50Z` while host wall-clock
  was `15:51Z`). A naive `@timestamp >= now-3m` against the host clock finds ZERO
  events on a healthy host. So freshness is measured purely in ES-timestamp
  space: at gate start, snapshot each host's EXACT current max EID1 `@timestamp`
  (frozen, since VMs are off/restoring); then count EID1 docs STRICTLY NEWER than
  that mark. A frozen/exited host yields 0 (correctly unhealthy); a live host
  accumulates new docs. NO guard subtraction — subtracting a window would re-count
  pre-existing docs and let an EXITED host falsely pass (caught and removed during
  testing: an early `--baseline-guard-sec 300` variant reported a stopped dc01 as
  "5 OK").
- **Active WinRM heartbeat.** An idle Windows VM emits almost no EID1 once the
  boot storm settles. So each poll the gate spawns 15 short-lived `cmd.exe /c ver`
  processes per not-yet-healthy host over WinRM. If the agent+Sysmon chain is
  live, those surface as fresh EID1 within seconds. This makes the gate a true
  end-to-end probe of the FULL chain: `WinRM reachable -> process spawned ->
  Sysmon EID1 -> Fleet -> Elasticsearch` — the precise chain that was silently
  broken before. `--no-heartbeat` falls back to passive boot-storm reliance.
- **WinRM is part of health.** Tracking EID1 alone let a Sysmon-shipping-but-
  WinRM-down host pass and then fail every routed playbook (observed: ws02 shipped
  186 fresh EID1 from its boot storm while WinRM was still `down:ConnectionError`,
  and the 6-playbook smoke run then failed all 3 ws02 playbooks with
  `HTTPConnectionPool(host=<ws02-ip>, port=5985): Max retries`). Requiring the
  WinRM heartbeat `ok` closes that gap for free.
- **EID field shape.** `winlog.event_id` and `event.code` are STRING fields ("1")
  in `logs-windows.sysmon_operational-default`; the gate `should`-matches both.

**Verification — works Y/N: YES.** Proven on a real restore→boot→gate cycle. Final
clean pass (all 3 VMs up):

```
poll 1: dc01=eid1:0/winrm:ok   ws01=eid1:2/winrm:ok    ws02=eid1:1/winrm:ok
poll 2: dc01=eid1:0/winrm:ok   ws01=eid1:19/winrm:ok H ws02=eid1:21/winrm:ok H
poll 5: dc01=eid1:37/winrm:ok H ws01=eid1:41/winrm:ok H ws02=eid1:41/winrm:ok H
ALL HOSTS HEALTHY (EID1 shipping + WinRM reachable). Gate PASSED.  EXIT=0
```

dc01 (a Domain Controller) is the slowest EID1 shipper — its heartbeat surfaced at
poll 5 (~2.5 min). The 20-min sweep timeout absorbs this comfortably. The gate
ALSO correctly FAILED (exit 1) when dc01 was stopped (eid1:0) and when ws02's
QEMU had crashed (winrm down) — it does not pass on a dead host.

---

## 2. Improved window extraction (Task 2) — `c2_naive_helper.py prepare-v2`

New subcommand (the proven `prepare`/`score` paths are untouched — v1 windows stay
reproducible). Output schema is IDENTICAL to v1 (`window_id`-keyed, labels withheld
in the `ground_truth.jsonl` side-file), so `score` is unchanged. Adds one field:
`n_eid1`.

**Change:** per playbook window, instead of a flat chronological top-60 (which let
EID12/13 registry noise crowd out process-creates), `prepare-v2`:
1. fetches ALL EID1 process-creation docs in the padded window (cap
   `--eid1-candidate-cap 120`) and ALWAYS includes them;
2. then fills with non-EID1 events chronologically up to `--max-events-per-window`
   (default **120**, up from 60);
3. widens window padding to **±120s** (up from ±60s) to absorb agent/Sysmon ingest
   lag and the VM clock skew.

**Verification — verifies Y/N: YES.** On the signal-rich interleaved/steg run
`20260528T091131Z-6bd91b` (telemetry already in ES), v2 vs v1:

| extraction       | windows | windows w/ EID1 | EID1 events captured |
|------------------|---------|-----------------|----------------------|
| v1 (flat-60)     | 182     | 161             | 1,200                |
| v2 (EID1-prior.) | 182     | **182**         | **20,323**           |

**~17x more EID1 captured**, and EID1 now present in every window. Sample malicious
window under v2 (`w0005`, `bitsadmin-mal-01-advanced-01-ps-bits.json`) contains the
real attack process-creation chain that v1 lost:

```
EID1 winrshost.exe  <- svchost.exe   WinrsHost.exe -Embedding
EID1 cmd.exe        <- winrshost.exe cmd.exe /C powershell -encodedcommand TgBlAHcA...
EID1 powershell.exe <- cmd.exe       powershell -encodedcommand TgBlAHcA...
```

This is the WinRM-driven LOLBin chain. Caveat: on signal-STARVED runs (control /
pre-burst) many LOLBin process-creates were never logged by Sysmon (the EID1 gap),
so those windows still show mostly OS-maintenance EID1 even under v2 — v2 captures
all that exists, it cannot create missing docs.

---

## 3. Health-gated full sweep (Task 3) — `scripts/lab-run-sweep-v2-gated.sh`

Per condition: restore clean -> settle 90s -> **watchdog** (docker-start any exited
VM container; mitigates the ws02 QEMU crash) -> **health gate** (block until all 3
hosts EID1+WinRM healthy; up to 3 gate attempts with watchdog between) -> execute
orchestrator. Restores between conditions for structural isolation. Output under a
NEW dir `results/attack-v2/<run_id>/` (via `MASHUNT_RESULTS_ROOT` env override added
to the orchestrator — one-line, surgical) so the prior `results/attack` dataset is
never clobbered.

**Conditions (10):** control `none/mixed` first, then the adversarial matrix
3 modes × 3 tiers (pre-burst / per-attack-burst / interleaved × overt / encoded /
steganographic).

**Faithful params:** `--profile full`, `--vms dc01,ws01,ws02`, `--burst-size 5`,
`--interleave-count 1`, `--pre-burst-size 200` (adversarial; control uses none),
185 playbooks (`--max-playbooks 0`).

**Launched DETACHED.**
- Sweep process PID (live): **318307** (`bash scripts/lab-run-sweep-v2-gated.sh`)
- Sweep log: `/home/user/mashunt-lab/results/attack-v2/sweep-v2-20260529T163244Z.log`
- Per-condition artifacts: `/home/user/mashunt-lab/results/attack-v2/<run_id>/`
- Started condition 1/10 (control none/mixed) at 2026-05-29T16:32:44Z.

**ETA:** control ~50 min + 3 pre-burst ~50 min each + 3 per-attack-burst ~85 min
each + 3 interleaved ~80 min each, plus ~5-10 min restore+gate per condition.
≈ **11-14 hours** wall time for all 10 conditions.

---

## 4. Smoke test of the full pipeline (restore -> gate -> 6 playbooks -> extract)

Ran the brief's `--max-playbooks 6` integration test (control mode):
- Restore succeeded (all 3 VMs reflink-restored + restarted).
- Gate passed on the real restore (all 3 hosts reached EID1+WinRM healthy in ~75s
  on the first cycle; dc01 a touch slower on later cycles).
- Orchestrator ran 6 playbooks in 264s; `results/attack-v2/20260529T161401Z-e08aa5/`.
- **Surfaced the ws02 QEMU crash**: on that cycle ws02's WinRM had not yet come up
  (QEMU assertion → container exit), so the 3 ws02-routed playbooks failed
  (`Max retries`/`copy failed`). This is what drove the WinRM-in-health-gate fix
  and the sweep watchdog. After `docker start mashunt-ws02`, ws02 came fully
  healthy (EID1 + WinRM ok) and the final gate passed 3/3.
- v2 extraction on the 3 successful (ws01) windows: all 3 carry EID1 process-
  creation (`n_eid1` 6/4/7). The control malicious window shows OS-maintenance EID1
  only (EID1 gap on signal-starved runs, as expected and documented).

---

## 5. Re-extraction plan (Task 4) and validity verification (Task 5)

These run AFTER each sweep run completes (the orchestrator monitor will drive
them; this section is the contract):

- **Task 4 — re-extract windows v2** for every new `attack-v2/<run_id>`:
  ```
  uv run scripts/eval/c2_naive_helper.py prepare-v2 \
    --run-dir results/attack-v2/<run_id> \
    --output results/_matrix-windows-v2/<run_id>/windows.jsonl
  ```
  writes `windows.jsonl` (+ `n_eid1`) and the `ground_truth.jsonl` side-file
  (labels withheld, window_id-keyed). `results/_matrix-windows-v2/` is created.

- **Task 5 — per-run telemetry-validity table** (to be filled as runs land):

  | run_id | mode/tier | hosts shipped (dc01/ws01/ws02) | mal-windows w/ attack EID1 | exit_code=0 frac | FLAG |
  |--------|-----------|-------------------------------|----------------------------|------------------|------|
  | _(pending — sweep in progress)_ | | | | | |

  For each run, verification confirms: (a) host.name distribution in ES during the
  run window shows all 3 hosts > 0; (b) a sample of malicious-playbook windows
  contains attack process-creation (EID1 with LOLBin or winrshost/powershell/cmd
  chain); (c) playbook exit_code=0 fraction. Any run still missing ws02 or attack
  EID1 is FLAGGED.

---

## 6. Final status

| Item | Status |
|------|--------|
| Health gate works | **YES** — proven on real restore, 3/3 healthy, EXIT=0; correctly FAILS on dead/WinRM-down host |
| Per-host EID1 at pass | dc01=37, ws01=41, ws02=41 fresh EID1 (+ WinRM ok all 3) |
| Extraction fix verifies | **YES** — 17x more EID1 (1,200→20,323), attack chain captured on signal-rich run |
| Full sweep launched | **YES** — detached, PID 318307, log `results/attack-v2/sweep-v2-20260529T163244Z.log` |
| ETA | ~11-14 h for all 10 conditions |
| Output dir (no clobber) | `results/attack-v2/<run_id>/` (+ `_matrix-windows-v2/<run_id>/` after extraction) |

**Blocker / flag (not hard):** `mashunt-ws02` QEMU is intermittently unstable
(monitor assertion → container exit shortly after boot). The sweep watchdog +
WinRM-aware gate + 3-attempt gate retry mitigate it (auto `docker start` + re-gate),
but a ws02 crash MID-RUN (after the gate passes) would still lose that run's
ws02-routed playbooks. The Task-5 validity check is the backstop — any run missing
ws02 telemetry is FLAGGED for targeted re-run. The lab host is RAM-tight (62 GB
total; ~57 GB used with 3 Windows VMs + full ELK), which likely aggravates the
QEMU race during the 3-VM boot storm (load peaked ~110 during simultaneous boot).

**Files (all on lab `/home/user/mashunt-lab`):**
- `scripts/eval/telemetry_health_gate.py` (new)
- `scripts/eval/c2_naive_helper.py` (added `prepare-v2`)
- `scripts/lab-attack-orchestrator.py` (added `MASHUNT_RESULTS_ROOT` override)
- `scripts/lab-run-sweep-v2-gated.sh` (new)
- Local copies: `/Users/user/mestrado/.orchestration/scratch/`

---

## 7. R1b — CRASH HARDENING (after the box OOM-died)

### 7.1 What crashed and why
The first v2 sweep booted dc01+ws01+ws02 SIMULTANEOUSLY each condition. The
3-VM boot storm spiked load to ~110 and RAM past headroom; with only a 4GB zram
swap (compressed RAM — useless under true memory pressure) the kernel OOM-killed
the box. It rebooted; ELK + the 3 setup containers came back (ES/Kibana/Fleet
healthy, `-setup` containers exited 0 normally); VM containers were Exited(255).

Before the crash, 2 v2 runs "completed" (control `74dc89`, pre-burst/overt
`11db59`) + 1 incomplete (`7068b7`, died ~playbook 94). **All 3 are INVALID** —
see 7.4 — and were moved to `results/attack-v2/_invalid-precrash/`.

### 7.2 Memory + swap (done)
- **ES heap 8g → 2g.** The env file had `ES_JAVA_OPTS=-Xms8g -Xmx8g` (8GB heap on
  a single-node lab!) and `ES_MEM_LIMIT=10GiB`. Lowered to `-Xms2g -Xmx2g` /
  4GiB limit; recreated ONLY the `elasticsearch` compose service (data volume
  intact). Verified: `heap_max_MB=2048`, cluster recovered to **yellow** (427
  active shards, replicas-unassigned = normal single-node). **ES heap lowered: YES.**
- **Disk swap +12GB.** zram alone was the trap. `/` is BTRFS so `fallocate`+swapon
  fails (`Invalid argument`); used `btrfs filesystem mkswapfile --size 12G
  /swapfile2 && swapon`. Total swap now 15GB (4 zram + 12 disk). **Swap added: YES.**

### 7.3 Staggered boots (the core fix, done + verified)
New `lab-snapshot.py restore-no-start` (stop all + restore disks, NO auto-start).
New gate `--hosts` flag gates ONE host. Rewrote `lab-run-sweep-v2-gated.sh`:
per condition → `restore-no-start` → boot **dc01 alone → gate dc01 → boot ws01 →
gate ws01 → boot ws02 → gate ws02** → orchestrate → extract. Each VM fully boots
and its agent checks in before the next starts, so the simultaneous boot storm
never happens. `boot_and_gate_one` retries a VM up to 3× (covers the ws02 QEMU
monitor-assertion crash).

**Staggered-boot verified on one full restore cycle (per-host EID1 at gate pass):**

| host | fresh EID1 at pass | WinRM | time to healthy |
|------|--------------------|-------|-----------------|
| dc01-server | **131** | ok | ~60s |
| ws01-client | **209** | ok | ~3.5 min (WinRM was the long pole) |
| ws02-client | **209** | ok | ~6 min, no QEMU crash |

Peak load ~11, RAM held ~22GB free, swap 0 used — nowhere near the OOM. **The
host that shipped ZERO before (dc01) ships 131 EID1 when booted alone** — proof
the dc01-zero was simultaneous-boot resource starvation, not an agent defect.
**Staggered-boot verified: YES.**

### 7.4 The 2 prior runs — VALID? **NO (both redone)**
Per-host telemetry in each run window (ES `host.name` distribution) + exec rates:

| run | mode/tier | dc01 / ws01 / ws02 (total docs) | exit0 frac | mal-win w/ attack EID1 | verdict |
|-----|-----------|--------------------------------|-----------|------------------------|---------|
| 74dc89 | none/mixed | **0** / 648 / 395 | 45.9% | 22.5% | **INVALID — dc01 ZERO** |
| 11db59 | pre-burst/overt | **0** / 458 / 488 | 57.3% | 0.0% | **INVALID — dc01 ZERO** |

dc01 shipped NOTHING in both (the box was already degrading toward the crash),
and exec success was poor (many WinRM failures). Both moved to
`_invalid-precrash/` and are being REDONE by the fresh full sweep (START=1, all 10
conditions). **Prior runs valid: NO.**

### 7.5 Relaunch (done)
Full 10-condition staggered sweep relaunched DETACHED:
- Sweep PID: **90524**
- Log: `/home/user/mashunt-lab/results/attack-v2/sweep-v2-20260529T191548Z.log`
- Conditions: **all 10** (control none/mixed + 3×3 adversarial), START=1.
- Faithful params: profile full, vms dc01,ws01,ws02, burst 5, interleave 1,
  pre-burst 200, 185 playbooks; per-condition restore→staggered-gate→orchestrate→
  `prepare-v2` → `results/_matrix-windows-v2/<run_id>/`.
- **Remaining conditions: 10** (all redone from scratch — the 2 pre-crash runs were
  invalid).
- **ETA: ~13-16 h.** Staggered boots add ~8-12 min/condition (3 sequential gates
  vs 1 parallel), but eliminate the crash. Net safer and only modestly slower.

### 7.6 New/changed files for R1b
- `scripts/lab-snapshot.py` — added `restore-no-start` action.
- `scripts/eval/telemetry_health_gate.py` — added `--hosts` (per-host gating);
  heartbeat bumped to 15 spawns.
- `scripts/lab-run-sweep-v2-gated.sh` — rewritten for staggered boots + per-condition
  `prepare-v2` extraction.
- env file: `ES_JAVA_OPTS`/`ES_MEM_LIMIT` lowered; `/swapfile2` (12GB) added.

**Residual risk:** ws02's QEMU monitor assertion can still crash it mid-run (after
its gate passes). The `boot_and_gate_one` retry only covers the boot phase; a
crash during playbook execution would lose ws02 playbooks for that run. Backstop:
the Task-5 validity check (`/tmp/validity_check.py` on lab; local copy in scratch)
flags any run with a missing host — those get a targeted re-run. The staggered low
load makes the crash much less likely than under the boot storm.
