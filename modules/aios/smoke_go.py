"""Smoke test for the AIOS go runtime (Volume 12, Fase 20).

Go is not installed in this environment, so this exercises the graceful
degradation path plus ACL enforcement (checked before CLI spawn). Run from
repo root:

    python modules/aios/smoke_go.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.aios import (  # noqa: E402
    GoRuntime,
    GoUnavailableError,
    KernelPermissionDeniedError,
    get_go_runtime,
    get_kernel_security,
)


def _assert(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {label}")
    print(f"  ok - {label}")


async def main() -> int:
    runtime: GoRuntime = get_go_runtime()

    security = get_kernel_security()
    security.grant("go", "inspect", "modules", "build", "test")

    # --- ACL (enforced before the CLI is spawned) ------------------------------------
    security.revoke("go", "build")
    try:
        await runtime.build.build()
        _assert(False, "ACL denies revoked build action")
    except KernelPermissionDeniedError:
        _assert(True, "ACL denies revoked build action")
    security.grant("go", "build")

    # --- degradation path (go not installed) -------------------------------------------
    _assert(not await runtime.available(), "available() is False without the go CLI")
    try:
        await runtime.version()
        _assert(False, "go unavailable raises GoUnavailableError")
    except GoUnavailableError:
        _assert(True, "go unavailable raises GoUnavailableError")

    # --- managers degrade consistently ---------------------------------------------------
    try:
        await runtime.modules.list()
        _assert(False, "modules degrade with GoUnavailableError")
    except GoUnavailableError:
        _assert(True, "modules degrade with GoUnavailableError")
    try:
        await runtime.test.run()
        _assert(False, "test degrade with GoUnavailableError")
    except GoUnavailableError:
        _assert(True, "test degrade with GoUnavailableError")

    # --- snapshot ----------------------------------------------------------------------------
    snap = await runtime.snapshot()
    _assert("go" in snap and snap["go"] is None, "snapshot degrades go to None")

    print("\nSMOKE OK — AIOS Go (degradation path)")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
