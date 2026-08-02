"""PowerShell client — spawns pwsh or Windows PowerShell without SDK deps."""
from __future__ import annotations

import asyncio
import shutil
from time import monotonic
from typing import Any

from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.kernel.kernel_security import (
    KernelPermissionDeniedError,
    get_kernel_security,
)


class PowerShellUnavailableError(RuntimeError):
    """Raised when the requested PowerShell binary cannot be reached."""


def require_powershell_action(action: str) -> None:
    """Enforce the ``powershell:<action>`` ACL before any privileged operation."""
    if not get_kernel_security().allow("powershell", action):
        raise KernelPermissionDeniedError("powershell", action)


class PowerShellClient:
    """Runs PowerShell scripts with pwsh or the Windows PowerShell host.

    ``binary`` is resolved through PATH; on Windows the classic host is
    ``powershell.exe`` while pwsh is the cross-platform edition.
    """

    def __init__(self, binary: str) -> None:
        self.binary = binary
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    async def _run(
        self, args: list[str], *, timeout_s: float = 120.0, cwd: str | None = None
    ) -> tuple[int, str, str]:
        started = monotonic()
        resolved = shutil.which(self.binary)
        try:
            proc = await asyncio.create_subprocess_exec(
                resolved or self.binary,
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )
        except (FileNotFoundError, OSError) as exc:
            raise PowerShellUnavailableError(
                f"{self.binary} CLI not found: {self.binary}"
            ) from exc
        try:
            out_b, err_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
        except TimeoutError:
            proc.kill()
            raise PowerShellUnavailableError(
                f"{self.binary} script timed out after {timeout_s}s"
            ) from None
        stdout = out_b.decode("utf-8", errors="replace")
        stderr = err_b.decode("utf-8", errors="replace")
        self._metrics.record_timing(f"powershell.{self.binary}.cli", monotonic() - started)
        code = int(proc.returncode or 0)
        self._logger.log("powershell", f"cli: {self.binary} script -> {code}")
        return code, stdout, stderr

    async def version(self) -> dict[str, Any]:
        require_powershell_action("inspect")
        code, out, err = await self._run(
            ["-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"],
            timeout_s=60.0,
        )
        if code != 0:
            raise PowerShellUnavailableError(
                f"{self.binary} version failed: {err.strip() or out.strip()}"
            )
        return {"version": out.strip()}

    async def ping(self) -> bool:
        try:
            code, _, _ = await self._run(["-NoProfile", "-Command", "1"], timeout_s=30.0)
            return code == 0
        except PowerShellUnavailableError:
            return False

    async def exec(
        self, command: str, *, cwd: str | None = None
    ) -> dict[str, Any]:
        require_powershell_action("exec")
        code, out, err = await self._run(
            ["-NoProfile", "-Command", command], cwd=cwd
        )
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}


__all__ = [
    "PowerShellClient",
    "PowerShellUnavailableError",
    "require_powershell_action",
]
