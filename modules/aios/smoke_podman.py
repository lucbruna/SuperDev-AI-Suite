"""Smoke test for the AIOS podman integration (Volume 12, Fase 15).

Podman exposes a docker-compatible CLI. On machines without podman this smoke
verifies the graceful-degradation path (available()==False, version() raises
PodmanUnavailableError, snapshot reports unavailable); with podman installed
it exercises the real CLI. Run from repo root:

    python modules/aios/smoke_podman.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.aios import (  # noqa: E402
    KernelPermissionDeniedError,
    PodmanRuntime,
    PodmanUnavailableError,
    get_kernel_security,
    get_podman_runtime,
)


def _assert(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {label}")
    print(f"  ok - {label}")


async def main() -> int:
    runtime: PodmanRuntime = get_podman_runtime()

    # --- ACL ---------------------------------------------------------------
    security = get_kernel_security()
    security.grant("podman", "run", "inspect")

    if await runtime.available():
        # Real podman engine present — exercise the live CLI.
        version = await runtime.client.version()
        _assert(isinstance(version, dict), "client version returns a dict")
        snap = await runtime.snapshot()
        _assert(snap["available"] is True, "snapshot reports podman available")
        print("\nSMOKE OK — AIOS Podman")
        return 0

    # --- graceful degradation (podman CLI absent) ---------------------------------
    print("  note - podman CLI not found; verifying graceful degradation")
    _assert(await runtime.available() is False, "available() is False without podman")

    try:
        await runtime.client.version()
        _assert(False, "version() raises PodmanUnavailableError")
    except PodmanUnavailableError:
        _assert(True, "version() raises PodmanUnavailableError")

    snap = await runtime.snapshot()
    _assert(snap["available"] is False, "snapshot reports podman unavailable")
    _assert(snap["version"] == {}, "snapshot version degrades to {}")

    security.revoke("podman", "run")
    try:
        await runtime.run("alpine:3.19", "echo", "hi")
        _assert(False, "ACL denies revoked run action")
    except KernelPermissionDeniedError:
        _assert(True, "ACL denies revoked run action")
    security.grant("podman", "run")

    print("\nSMOKE OK — AIOS Podman (degradation path)")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
