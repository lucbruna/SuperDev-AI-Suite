"""pnpm package manager wrapper for the AIOS node runtime."""
from __future__ import annotations

from typing import Any

from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.node.node_client import (
    require_node_action,
    run_cli,
)


class PnpmUnavailableError(RuntimeError):
    """Raised when the pnpm CLI cannot be reached."""


class PnpmManager:
    """Fast, disk-efficient alternative to npm backed by the pnpm CLI."""

    def __init__(self, binary: str = "pnpm") -> None:
        self.binary = binary

    async def _run(
        self, args: list[str], *, timeout_s: float = 300.0, cwd: str | None = None
    ) -> tuple[int, str, str]:
        return await run_cli(
            self.binary, args, component="pnpm", timeout_s=timeout_s, cwd=cwd,
            missing=PnpmUnavailableError,
        )

    async def version(self) -> dict[str, Any]:
        require_node_action("pnpm")
        code, out, err = await self._run(["--version"], timeout_s=30.0)
        if code != 0:
            raise PnpmUnavailableError(
                f"pnpm --version failed: {err.strip() or out.strip()}"
            )
        return {"version": out.strip()}

    async def install(
        self,
        package: str | None = None,
        *,
        cwd: str | None = None,
        dev: bool = False,
    ) -> dict[str, Any]:
        require_node_action("pnpm")
        args = ["add" if package else "install"]
        if dev:
            args.append("--save-dev")
        if package:
            args.append(package)
        code, out, err = await self._run(args, cwd=cwd)
        get_kernel_metrics().increment("node.pnpm.install")
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}

    async def run_script(self, name: str, *, cwd: str | None = None) -> dict[str, Any]:
        require_node_action("pnpm")
        code, out, err = await self._run(["run", name], cwd=cwd)
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}


__all__ = ["PnpmManager", "PnpmUnavailableError"]
