"""Go client — spawns the go CLI without SDK dependencies."""
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


class GoUnavailableError(RuntimeError):
    """Raised when the go CLI cannot be reached (not installed)."""


def require_go_action(action: str) -> None:
    """Enforce the ``go:<action>`` ACL before any privileged operation."""
    if not get_kernel_security().allow("go", action):
        raise KernelPermissionDeniedError("go", action)


class GoClient:
    """Minimal go wrapper: version and ping with graceful degradation."""

    def __init__(self, binary: str = "go") -> None:
        self.binary = binary
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    async def _run(
        self, args: list[str], *, timeout_s: float = 300.0, cwd: str | None = None
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
            raise GoUnavailableError(f"go CLI not found: {self.binary}") from exc
        try:
            out_b, err_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
        except TimeoutError:
            proc.kill()
            raise GoUnavailableError(
                f"go {' '.join(args[:3])} timed out after {timeout_s}s"
            ) from None
        stdout = out_b.decode("utf-8", errors="replace")
        stderr = err_b.decode("utf-8", errors="replace")
        self._metrics.record_timing("go.cli", monotonic() - started)
        code = int(proc.returncode or 0)
        self._logger.log("go", f"cli: go {' '.join(args[:3])} -> {code}")
        return code, stdout, stderr

    async def version(self) -> dict[str, Any]:
        require_go_action("inspect")
        code, out, err = await self._run(["version"], timeout_s=30.0)
        if code != 0:
            raise GoUnavailableError(f"go version failed: {err.strip() or out.strip()}")
        return {"version": out.strip()}

    async def ping(self) -> bool:
        try:
            code, _, _ = await self._run(["version"], timeout_s=30.0)
            return code == 0
        except GoUnavailableError:
            return False


__all__ = ["GoClient", "GoUnavailableError", "require_go_action"]
