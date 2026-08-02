"""Smoke test for the AIOS powershell runtime (Volume 12, Fase 24).

Exercises ACL, real Windows PowerShell 5.1 script execution (powershell.exe
is present on this host) and pwsh graceful degradation (not installed).
Run from repo root:

    python modules/aios/smoke_powershell.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.aios import (  # noqa: E402
    KernelPermissionDeniedError,
    PowerShellRuntime,
    PowerShellUnavailableError,
    get_kernel_security,
    get_powershell_runtime,
)


def _assert(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {label}")
    print(f"  ok - {label}")


async def main() -> int:
    runtime: PowerShellRuntime = get_powershell_runtime()

    security = get_kernel_security()
    security.grant("powershell", "inspect", "exec")

    # --- ACL ----------------------------------------------------------------------
    security.revoke("powershell", "exec")
    try:
        await runtime.windows_terminal.exec("Write-Output 'hi'")
        _assert(False, "ACL denies revoked exec action")
    except KernelPermissionDeniedError:
        _assert(True, "ACL denies revoked exec action")
    security.grant("powershell", "exec")

    # --- Windows PowerShell 5.1 (real) ----------------------------------------------
    _assert(await runtime.windows_terminal.ping(), "windows powershell is available")
    version = await runtime.windows_terminal.version()
    _assert(version.get("version"), "windows powershell reports a version")
    script = await runtime.windows_terminal.exec(
        "$a = 6 * 7; Write-Output ('hello aios ' + $a)"
    )
    _assert(script["ok"] and "hello aios 42" in script["stdout"], "powershell executes a script")

    # --- pwsh degradation (not installed) ----------------------------------------------
    _assert(not await runtime.pwsh.ping(), "pwsh unavailable -> ping False")
    try:
        await runtime.pwsh.exec("Write-Output 'hi'")
        _assert(False, "pwsh exec raises PowerShellUnavailableError")
    except PowerShellUnavailableError:
        _assert(True, "pwsh exec raises PowerShellUnavailableError")

    # --- snapshot ----------------------------------------------------------------------
    snap = await runtime.snapshot()
    _assert(
        "pwsh" in snap and "windows_powershell" in snap,
        "snapshot exposes powershell inventory",
    )

    print("\nSMOKE OK — AIOS PowerShell")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
