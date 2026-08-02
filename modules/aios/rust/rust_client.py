"""Rust client — spawns the cargo CLI without SDK dependencies."""
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


class RustUnavailableError(RuntimeError):
    """Raised when the cargo/rustc CLI cannot be reached (not installed)."""


def require_rust_action(action: str) -> None:
    """Enforce the ``rust:<action>`` ACL before any privileged operation."""
    if not get_kernel_security().allow("rust", action):
        raise KernelPermissionDeniedError("rust", action)


class CargoClient:
    """Spawns the ``cargo`` CLI as a subprocess (no SDK dependency)."""

    def __init__(self, binary: str = "cargo") -> None:
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
            raise RustUnavailableError(f"cargo CLI not found: {self.binary}") from exc
        try:
            out_b, err_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
        except TimeoutError:
            proc.kill()
            raise RustUnavailableError(
                f"cargo {' '.join(args[:3])} timed out after {timeout_s}s"
            ) from None
        stdout = out_b.decode("utf-8", errors="replace")
        stderr = err_b.decode("utf-8", errors="replace")
        self._metrics.record_timing("rust.cli", monotonic() - started)
        code = int(proc.returncode or 0)
        self._logger.log("rust", f"cli: cargo {' '.join(args[:3])} -> {code}")
        return code, stdout, stderr

    async def version(self) -> dict[str, Any]:
        require_rust_action("inspect")
        code, out, err = await self._run(["--version"], timeout_s=30.0)
        if code != 0:
            raise RustUnavailableError(
                f"cargo --version failed: {err.strip() or out.strip()}"
            )
        return {"version": out.strip()}

    async def ping(self) -> bool:
        try:
            code, _, _ = await self._run(["--version"], timeout_s=30.0)
            return code == 0
        except RustUnavailableError:
            return False


__all__ = ["CargoClient", "RustUnavailableError", "require_rust_action"]
