"""Smoke test for the AIOS rust runtime (Volume 12, Fase 21).

Cargo is not installed in this environment, so this exercises the graceful
degradation path plus ACL enforcement (checked before CLI spawn). Run from
repo root:

    python modules/aios/smoke_rust.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.aios import (  # noqa: E402
    KernelPermissionDeniedError,
    RustRuntime,
    RustUnavailableError,
    get_kernel_security,
    get_rust_runtime,
)


def _assert(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {label}")
    print(f"  ok - {label}")


async def main() -> int:
    runtime: RustRuntime = get_rust_runtime()

    security = get_kernel_security()
    security.grant("rust", "inspect", "cargo", "clippy")

    # --- ACL (enforced before the CLI is spawned) ------------------------------------
    security.revoke("rust", "clippy")
    try:
        await runtime.clippy.run()
        _assert(False, "ACL denies revoked clippy action")
    except KernelPermissionDeniedError:
        _assert(True, "ACL denies revoked clippy action")
    security.grant("rust", "clippy")

    # --- degradation path (cargo not installed) -------------------------------------------
    _assert(not await runtime.available(), "available() is False without the cargo CLI")
    try:
        await runtime.version()
        _assert(False, "cargo unavailable raises RustUnavailableError")
    except RustUnavailableError:
        _assert(True, "cargo unavailable raises RustUnavailableError")

    try:
        await runtime.cargo.test()
        _assert(False, "cargo test degrades with RustUnavailableError")
    except RustUnavailableError:
        _assert(True, "cargo test degrades with RustUnavailableError")

    # --- snapshot ----------------------------------------------------------------------------
    snap = await runtime.snapshot()
    _assert("cargo" in snap and snap["cargo"] is None, "snapshot degrades cargo to None")

    print("\nSMOKE OK — AIOS Rust (degradation path)")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
