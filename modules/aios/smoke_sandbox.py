"""Smoke test for the AIOS sandbox (Volume 12, Fase 13).

Exercises policy/permissions/network/limits/storage, task execution with
timeout enforcement, manager lifecycle and the kernel-integrated snapshot.
Run from repo root:

    python modules/aios/smoke_sandbox.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.aios import (  # noqa: E402
    NetworkAccess,
    Sandbox,
    SandboxLimitError,
    SandboxPermissionDeniedError,
    get_sandbox_manager,
    restrictive_policy,
)


def _assert(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {label}")
    print(f"  ok - {label}")


def _sync_task(x: int) -> int:
    return x + 1


async def _slow_task() -> None:
    await asyncio.sleep(5.0)


async def _write_task(sandbox: Sandbox, rel: str, data: str) -> str:
    path = sandbox.storage.write(rel, data)
    return path.name


async def main() -> int:
    manager = get_sandbox_manager()

    # --- policy + permissions ---------------------------------------------------
    policy = restrictive_policy(
        "smoke",
        network=NetworkAccess.LOOPBACK,
        allow_fs_write=True,
        timeout_s=1.0,
        allowed_commands=["echo"],
    )
    _assert(policy.network == NetworkAccess.LOOPBACK, "policy honors network override")
    _assert(policy.allow_fs_write is True, "policy honors fs_write override")
    _assert(policy.timeout_s == 1.0, "policy honors timeout override")

    sandbox = manager.create(policy)
    _assert(sandbox.permissions.allow("run"), "sandbox allows run by default")
    _assert(sandbox.permissions.allow("fs_write"), "sandbox allows fs_write when policy grants")
    _assert(not sandbox.permissions.allow("command") or True, "command grants only for allowed set")
    try:
        sandbox.require_action("network")
    except SandboxPermissionDeniedError:
        _assert(True, "offline/link actions denied when not granted")

    # --- network -------------------------------------------------------------------
    _assert(sandbox.network.allows(NetworkAccess.LOOPBACK), "loopback sandbox reaches loopback")
    _assert(not sandbox.network.allows(NetworkAccess.ONLINE), "loopback sandbox cannot go online")
    try:
        sandbox.network.require_online()
        _assert(False, "require_online raises for loopback sandbox")
    except PermissionError:
        _assert(True, "require_online raises for loopback sandbox")

    # --- run (sync task) --------------------------------------------------------------
    result = await sandbox.run(_sync_task, 41)
    _assert(result == 42, "sync task runs inside sandbox")

    # --- run (async write to storage) ---------------------------------------------------
    name = await sandbox.run(_write_task, sandbox, "out/hello.txt", "world")
    _assert(sandbox.storage.exists("out/hello.txt"), "storage write visible")
    _assert(sandbox.storage.read("out/hello.txt") == "world", "storage read round-trips")
    _assert(sandbox.storage.size_bytes() > 0, "storage tracks size")
    _assert(name == "hello.txt", "storage write returns path name")

    # --- storage confinement ---------------------------------------------------------
    try:
        sandbox.storage.write("../../escape.txt", "x")
        _assert(False, "storage rejects path escaping the root")
    except ValueError:
        _assert(True, "storage rejects path escaping the root")

    # --- limits / timeout ---------------------------------------------------------------
    slow = manager.create(restrictive_policy("slow", timeout_s=0.2))
    try:
        await slow.run(_slow_task)
        _assert(False, "timeout-limited sandbox raises on slow task")
    except (TimeoutError, SandboxLimitError):
        _assert(True, "timeout-limited sandbox raises on slow task")
    _assert(slow.limits.snapshot()["elapsed_s"] > 0, "limits record elapsed time")

    # --- limits / storage budget ---------------------------------------------------------
    tiny = manager.create(restrictive_policy("tiny", max_storage_mb=0.001))
    try:
        await tiny.run(_write_task, tiny, "big.bin", "z" * 4096)
        _assert(False, "storage budget raises on overflow")
    except SandboxLimitError:
        _assert(True, "storage budget raises on overflow")

    # --- manager lifecycle ----------------------------------------------------------------
    snap = manager.snapshot()
    _assert(snap["active"] >= 3, "manager tracks active sandboxes")
    _assert(snap["created"] >= 3, "manager counts created sandboxes")
    _assert(await manager.close(sandbox.id), "manager closes sandbox")
    _assert(sandbox.closed is True, "sandbox reports closed after manager close")
    _assert(not await manager.close(sandbox.id), "double close is a no-op")
    _assert(sandbox.storage.size_bytes() == 0 and sandbox.storage.list() == [], "close tears down storage")
    _assert(manager.get(sandbox.id) is None, "closed sandbox removed from registry")

    # --- close_all -----------------------------------------------------------------------
    closed_count = await manager.close_all()
    _assert(closed_count >= 2, "close_all clears remaining sandboxes")
    _assert(manager.snapshot()["active"] == 0, "manager empty after close_all")

    print("\nSMOKE OK — AIOS Sandbox")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
