"""Shell client — spawns POSIX shell CLIs (bash/zsh/fish) without SDK deps."""
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


class ShellUnavailableError(RuntimeError):
    """Raised when the requested shell binary cannot be reached."""


def require_shell_action(action: str) -> None:
    """Enforce the ``shell:<action>`` ACL before any privileged operation."""
    if not get_kernel_security().allow("shell", action):
        raise KernelPermissionDeniedError("shell", action)


class ShellClient:
    """Runs scripts with a POSIX shell (bash/zsh/fish).

    On Windows the shell shim is often ``bash.exe`` from Git for Windows; the
    binary name is resolved through PATH, so no hardcoded paths are used.
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
            raise ShellUnavailableError(
                f"{self.binary} CLI not found: {self.binary}"
            ) from exc
        try:
            out_b, err_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
        except TimeoutError:
            proc.kill()
            raise ShellUnavailableError(
                f"{self.binary} script timed out after {timeout_s}s"
            ) from None
        stdout = out_b.decode("utf-8", errors="replace")
        stderr = err_b.decode("utf-8", errors="replace")
        self._metrics.record_timing(f"shell.{self.binary}.cli", monotonic() - started)
        code = int(proc.returncode or 0)
        self._logger.log("shell", f"cli: {self.binary} script -> {code}")
        return code, stdout, stderr

    async def version(self) -> dict[str, Any]:
        require_shell_action("inspect")
        code, out, err = await self._run(["--version"], timeout_s=30.0)
        if code != 0:
            raise ShellUnavailableError(
                f"{self.binary} --version failed: {err.strip() or out.strip()}"
            )
        return {"version": out.strip().splitlines()[0]}

    async def ping(self) -> bool:
        try:
            code, _, _ = await self._run(["--version"], timeout_s=30.0)
            return code == 0
        except ShellUnavailableError:
            return False

    async def exec(
        self, script: str, *, cwd: str | None = None
    ) -> dict[str, Any]:
        require_shell_action("exec")
        code, out, err = await self._run(["-c", script], cwd=cwd)
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}

    async def run_file(self, path: str, *, cwd: str | None = None) -> dict[str, Any]:
        require_shell_action("exec")
        code, out, err = await self._run([str(path)], cwd=cwd)
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}


__all__ = ["ShellClient", "ShellUnavailableError", "require_shell_action"]
