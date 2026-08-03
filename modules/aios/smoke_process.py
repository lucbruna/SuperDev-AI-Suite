"""Smoke test for the AIOS process runtime (Volume 12, Fase 27).

Exercises ACL, process spawn/execute, pool, monitor, tree, and cleanup.
Run from repo root:

    python modules/aios/smoke_process.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.aios import (  # noqa: E402
    KernelPermissionDeniedError,
    get_kernel_security,
    get_process_runtime,
)


def _assert(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {label}")
    print(f"  ok - {label}")


async def main() -> int:
    runtime = get_process_runtime()

    security = get_kernel_security()
    security.grant("process", "spawn", "execute", "terminate", "monitor", "tree", "cleanup", "pool_start", "pool_submit", "pool_shutdown")

    # --- ACL ----------------------------------------------------------------------
    security.revoke("process", "execute")
    try:
        await runtime.executor.run(["echo", "hi"])
        _assert(False, "ACL denies revoked execute action")
    except KernelPermissionDeniedError:
        _assert(True, "ACL denies revoked execute action")
    security.grant("process", "execute")

    # --- executor -----------------------------------------------------------------
    result = await runtime.executor.run(["cmd", "/c", "echo hello process"])
    _assert(result.returncode == 0 and "hello process" in result.stdout, "executor runs command")
    _assert(result.pid > 0, "executor returns PID")

    # --- manager ------------------------------------------------------------------
    info = await runtime.manager.spawn(["cmd", "/c", "echo manager test"])
    _assert(info.pid > 0 and info.cmd == ["cmd", "/c", "echo manager test"], "manager spawns process")
    waited = await runtime.manager.wait(info.pid, timeout=5.0)
    _assert(waited.returncode == 0, "manager waits for completion")

    # --- pool ---------------------------------------------------------------------
    await runtime.pool.start()
    _assert(len(runtime.pool._workers) > 0, "pool starts workers")
    pool_result = await runtime.pool.submit(asyncio.sleep, 0, result="pool ok")
    _assert(pool_result == "pool ok", "pool submits task")
    await runtime.pool.shutdown()
    _assert(len(runtime.pool._workers) == 0, "pool shuts down")

    # --- monitor ------------------------------------------------------------------
    import os

    snap = runtime.monitor.snapshot(os.getpid())
    _assert(snap is not None and snap.pid == os.getpid(), "monitor snapshots PID")
    procs = runtime.monitor.list_system_processes("python")
    _assert(len(procs) > 0, "monitor lists system processes")

    # --- tree ---------------------------------------------------------------------
    tree = runtime.tree.build()
    _assert(isinstance(tree, list) and len(tree) > 0, "tree builds roots")
    found = runtime.tree.find_by_name("python", tree)
    _assert(len(found) > 0, "tree finds by name")

    # --- cleanup ------------------------------------------------------------------
    cleanup_result = await runtime.cleanup.cleanup_by_name("nonexistent_process_xyz")
    _assert(cleanup_result.terminated == [] and cleanup_result.failed == [], "cleanup handles no matches")

    # --- snapshot -----------------------------------------------------------------
    snap = await runtime.snapshot()
    _assert(snap["available"] is True, "snapshot reports available")

    print("\nSMOKE OK — AIOS Process")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
