"""Smoke test for the AIOS shell runtime (Volume 12, Fase 23).

Exercises ACL, a real bash script execution and zsh/fish graceful
degradation (not installed on this Windows host). Run from repo root:

    python modules/aios/smoke_shell.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.aios import (  # noqa: E402
    KernelPermissionDeniedError,
    ShellRuntime,
    ShellUnavailableError,
    get_kernel_security,
    get_shell_runtime,
)


def _assert(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {label}")
    print(f"  ok - {label}")


async def main() -> int:
    runtime: ShellRuntime = get_shell_runtime()

    security = get_kernel_security()
    security.grant("shell", "inspect", "exec")

    # --- ACL ----------------------------------------------------------------------
    security.revoke("shell", "exec")
    try:
        await runtime.bash.exec("echo hi")
        _assert(False, "ACL denies revoked exec action")
    except KernelPermissionDeniedError:
        _assert(True, "ACL denies revoked exec action")
    security.grant("shell", "exec")

    # --- bash (real, Git for Windows) ---------------------------------------------
    _assert(await runtime.bash.ping(), "bash is available")
    bash_version = await runtime.bash.version()
    _assert("bash" in bash_version.get("version", "").lower() or "GNU" in bash_version.get("version", ""),
            "bash reports a version")
    script = await runtime.bash.exec("echo hello aios && expr 6 '*' 7")
    _assert(script["ok"] and "hello aios" in script["stdout"], "bash executes a script")
    _assert("42" in script["stdout"], "bash script output is captured")

    # --- zsh / fish degradation ----------------------------------------------------
    _assert(not await runtime.zsh.ping(), "zsh unavailable -> ping False")
    try:
        await runtime.zsh.exec("echo hi")
        _assert(False, "zsh exec raises ShellUnavailableError")
    except ShellUnavailableError:
        _assert(True, "zsh exec raises ShellUnavailableError")
    _assert(not await runtime.fish.ping(), "fish unavailable -> ping False")

    # --- snapshot ----------------------------------------------------------------------
    snap = await runtime.snapshot()
    _assert("bash" in snap and "zsh" in snap and "fish" in snap, "snapshot exposes shell inventory")

    print("\nSMOKE OK — AIOS Shell")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
