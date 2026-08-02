"""Dotnet client — spawns the dotnet CLI without SDK dependencies."""
from __future__ import annotations

import asyncio
from time import monotonic
from typing import Any

from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.kernel.kernel_security import (
    KernelPermissionDeniedError,
    get_kernel_security,
)


class DotnetUnavailableError(RuntimeError):
    """Raised when the dotnet CLI cannot be reached."""


def require_dotnet_action(action: str) -> None:
    """Enforce the ``dotnet:<action>`` ACL before any privileged operation."""
    if not get_kernel_security().allow("dotnet", action):
        raise KernelPermissionDeniedError("dotnet", action)


class DotnetClient:
    """Spawns the ``dotnet`` CLI as a subprocess (no SDK dependency)."""

    def __init__(self, binary: str = "dotnet") -> None:
        self.binary = binary
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    async def _run(
        self, args: list[str], *, timeout_s: float = 600.0, cwd: str | None = None
    ) -> tuple[int, str, str]:
        started = monotonic()
        try:
            proc = await asyncio.create_subprocess_exec(
                self.binary,
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )
        except FileNotFoundError as exc:
            raise DotnetUnavailableError(
                f"dotnet CLI not found: {self.binary}"
            ) from exc
        try:
            out_b, err_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
        except TimeoutError:
            proc.kill()
            raise DotnetUnavailableError(
                f"dotnet {' '.join(args[:3])} timed out after {timeout_s}s"
            ) from None
        stdout = out_b.decode("utf-8", errors="replace")
        stderr = err_b.decode("utf-8", errors="replace")
        self._metrics.record_timing("dotnet.cli", monotonic() - started)
        code = int(proc.returncode or 0)
        self._logger.log("dotnet", f"cli: dotnet {' '.join(args[:3])} -> {code}")
        return code, stdout, stderr

    async def version(self) -> dict[str, Any]:
        require_dotnet_action("inspect")
        code, out, err = await self._run(["--version"], timeout_s=30.0)
        if code != 0:
            raise DotnetUnavailableError(
                f"dotnet --version failed: {err.strip() or out.strip()}"
            )
        return {"version": out.strip()}

    async def ping(self) -> bool:
        try:
            code, _, _ = await self._run(["--version"], timeout_s=30.0)
            return code == 0
        except DotnetUnavailableError:
            return False

    async def new(
        self, template: str, name: str, *, output: str | None = None
    ) -> dict[str, Any]:
        require_dotnet_action("new")
        args = ["new", template, "--name", name]
        if output:
            args += ["--output", output]
        code, out, err = await self._run(args, timeout_s=300.0)
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}

    async def run(self, *, cwd: str | None = None) -> dict[str, Any]:
        require_dotnet_action("run")
        code, out, err = await self._run(["run", "--no-launch-profile"], cwd=cwd)
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}


__all__ = ["DotnetClient", "DotnetUnavailableError", "require_dotnet_action"]
