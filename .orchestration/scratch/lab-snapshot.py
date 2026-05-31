# /// script
# requires-python = ">=3.11"
# dependencies = ["pywinrm>=0.4.3"]
# ///
"""Take/restore an `experiment-ready` snapshot of all 3 VM disks (BTRFS reflink).

Flow:
  1) Send clean ACPI shutdown to each Windows VM via WinRM.
  2) Wait for the corresponding docker container to enter `exited` state.
  3) Reflink-copy data.img + windows.vars + windows.boot to `<file>.experiment-ready`.
  4) `docker commit` each container as `mashunt/<container>:experiment-ready`
     (cosmetic — captures container metadata; disk state lives in the volume).
  5) Restart containers. Caller confirms VMs come back online.

Usage:
  uv run lab-snapshot.py create
  uv run lab-snapshot.py restore     # swaps live data.img with the snapshot
  uv run lab-snapshot.py list        # shows existing snapshot files
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import time

import winrm

LAB_VMS_FILE = pathlib.Path.home() / "mashunt-lab" / "lab-vms.json"
VM_VOL_ROOT = pathlib.Path("/home/user/fast-storage/vm-volumes")
VMS = ["dc01", "ws01", "ws02"]
SNAPSHOT_TAG = "experiment-ready"
SNAPSHOT_FILES = ["data.img", "windows.vars", "windows.boot"]


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def winrm_session(ip: str) -> winrm.Session:
    return winrm.Session(
        f"http://{ip}:5985/wsman",
        auth=("labadmin", "labadmin"),
        transport="ntlm",
    )


def graceful_shutdown(vm: str, ip: str) -> None:
    """Issue ACPI shutdown via WinRM."""
    print(f"  [{vm}] sending Stop-Computer -Force...")
    try:
        sess = winrm_session(ip)
        sess.run_ps("Stop-Computer -Force")
    except Exception as exc:
        print(
            f"  [{vm}] WinRM shutdown raised (expected, VM stops mid-call): {exc!s}"[
                :160
            ]
        )


def wait_container_stopped(container: str, timeout_sec: int = 180) -> bool:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        r = run(
            ["docker", "inspect", "-f", "{{.State.Status}}", container], check=False
        )
        status = r.stdout.strip()
        if status in {"exited", "dead"}:
            return True
        time.sleep(3)
    return False


def force_stop(container: str) -> None:
    print(f"  [{container}] forcing docker stop (timeout=60)...")
    run(["docker", "stop", "-t", "60", container], check=False)


def reflink_snapshot(vm: str) -> dict:
    """Reflink-copy each significant file in the VM volume."""
    src_dir = VM_VOL_ROOT / vm
    out: dict[str, str] = {}
    for fn in SNAPSHOT_FILES:
        src = src_dir / fn
        dst = src_dir / f"{fn}.{SNAPSHOT_TAG}"
        if not src.exists():
            out[fn] = "missing"
            continue
        run(["sudo", "cp", "--reflink=always", "-f", str(src), str(dst)])
        out[fn] = f"snapshotted ({src.stat().st_size:_} bytes)"
    return out


def restore_snapshot(vm: str) -> dict:
    src_dir = VM_VOL_ROOT / vm
    out: dict[str, str] = {}
    for fn in SNAPSHOT_FILES:
        snap = src_dir / f"{fn}.{SNAPSHOT_TAG}"
        live = src_dir / fn
        if not snap.exists():
            out[fn] = "no snapshot"
            continue
        run(["sudo", "cp", "--reflink=always", "-f", str(snap), str(live)])
        out[fn] = "restored"
    return out


def list_snapshots() -> dict:
    out: dict[str, dict] = {}
    for vm in VMS:
        d = VM_VOL_ROOT / vm
        out[vm] = {}
        for fn in SNAPSHOT_FILES:
            snap = d / f"{fn}.{SNAPSHOT_TAG}"
            if snap.exists():
                st = snap.stat()
                out[vm][fn] = {"size": st.st_size, "mtime": time.ctime(st.st_mtime)}
            else:
                out[vm][fn] = None
    return out


def docker_commit(container: str) -> str:
    tag = f"mashunt/{container}:{SNAPSHOT_TAG}"
    r = run(["docker", "commit", container, tag], check=False)
    return tag if r.returncode == 0 else f"FAIL: {r.stderr.strip()[:120]}"


def docker_start(container: str) -> str:
    r = run(["docker", "start", container], check=False)
    return r.stdout.strip() if r.returncode == 0 else f"FAIL: {r.stderr.strip()[:120]}"


def cmd_create() -> int:
    meta = json.loads(LAB_VMS_FILE.read_text())["vms"]

    print("=== Phase 1: graceful shutdown ===")
    for vm in VMS:
        graceful_shutdown(vm, meta[vm]["ip"])

    print("\n=== Phase 2: wait for containers to stop ===")
    for vm in VMS:
        c = meta[vm]["container_name"]
        if wait_container_stopped(c, 180):
            print(f"  {c}: stopped")
        else:
            force_stop(c)
            wait_container_stopped(c, 60)

    print("\n=== Phase 3: reflink snapshot ===")
    snap_results: dict[str, dict] = {}
    for vm in VMS:
        snap_results[vm] = reflink_snapshot(vm)
        print(f"  {vm}: {snap_results[vm]}")

    print("\n=== Phase 4: docker commit ===")
    commit_tags: dict[str, str] = {}
    for vm in VMS:
        c = meta[vm]["container_name"]
        commit_tags[c] = docker_commit(c)
        print(f"  {c}: {commit_tags[c]}")

    print("\n=== Phase 5: restart containers ===")
    for vm in VMS:
        c = meta[vm]["container_name"]
        out = docker_start(c)
        print(f"  {c}: started ({out})")

    print("\n=== Phase 6: write snapshot reference ===")
    ref = {
        "tag": SNAPSHOT_TAG,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "vms": {
            vm: {
                "files": snap_results[vm],
                "container_image": commit_tags.get(meta[vm]["container_name"]),
            }
            for vm in VMS
        },
    }
    ref_file = pathlib.Path.home() / "mashunt-lab" / ".snapshot-experiment-ready.json"
    ref_file.write_text(json.dumps(ref, indent=2))
    print(f"  reference written: {ref_file}")

    print("\nSnapshot complete. Restore via: uv run lab-snapshot.py restore")
    return 0


def cmd_restore() -> int:
    meta = json.loads(LAB_VMS_FILE.read_text())["vms"]

    print("=== Phase 1: stop containers ===")
    for vm in VMS:
        c = meta[vm]["container_name"]
        force_stop(c)
        wait_container_stopped(c, 60)

    print("\n=== Phase 2: restore snapshot ===")
    for vm in VMS:
        result = restore_snapshot(vm)
        print(f"  {vm}: {result}")

    print("\n=== Phase 3: restart containers ===")
    for vm in VMS:
        c = meta[vm]["container_name"]
        out = docker_start(c)
        print(f"  {c}: started ({out})")
    return 0


def cmd_restore_no_start() -> int:
    """Stop all + restore disks, but DO NOT start any container.

    The caller (staggered-boot flow) starts the VMs one at a time with a
    per-host health gate between each, so the 3-VM simultaneous boot storm —
    which spiked load to ~110 and OOM-crashed the box — never happens."""
    meta = json.loads(LAB_VMS_FILE.read_text())["vms"]

    print("=== Phase 1: stop containers ===")
    for vm in VMS:
        c = meta[vm]["container_name"]
        force_stop(c)
        wait_container_stopped(c, 60)

    print("\n=== Phase 2: restore snapshot (NO start) ===")
    for vm in VMS:
        result = restore_snapshot(vm)
        print(f"  {vm}: {result}")
    print("\nDisks restored. Containers left STOPPED for staggered boot.")
    return 0


def cmd_list() -> int:
    print(json.dumps(list_snapshots(), indent=2))
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["create", "restore", "restore-no-start", "list"])
    args = p.parse_args()
    return {
        "create": cmd_create,
        "restore": cmd_restore,
        "restore-no-start": cmd_restore_no_start,
        "list": cmd_list,
    }[args.action]()


if __name__ == "__main__":
    sys.exit(main())
