"""bun package manager and test runner for the AIOS node runtime."""
from __future__ import annotations

from typing import Any

from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.node.node_client import (
    require_node_action,
    run_cli,
)


class BunUnavailableError(RuntimeError):
    """Raised when the bun CLI cannot be reached."""


class BunManager:
    """Bundled runtime: installs packages and runs tests via the bun CLI."""

    def __init__(self, binary: str = "bun") -> None:
        self.binary = binary

    async def _run(
        self, args: list[str], *, timeout_s: float = 300.0, cwd: str | None = None
    ) -> tuple[int, str, str]:
        return await run_cli(
            self.binary, args, component="bun", timeout_s=timeout_s, cwd=cwd,
            missing=BunUnavailableError,
        )

    async def version(self) -> dict[str, Any]:
        require_node_action("bun")
        code, out, err = await self._run(["--version"], timeout_s=30.0)
        if code != 0:
            raise BunUnavailableError(
                f"bun --version failed: {err.strip() or out.strip()}"
            )
        return {"version": out.strip()}

    async def install(
        self, package: str | None = None, *, cwd: str | None = None, dev: bool = False
    ) -> dict[str, Any]:
        require_node_action("bun")
        if package:
            args = ["add", package]
            if dev:
                args.append("--dev")
        else:
            args = ["install"]
        code, out, err = await self._run(args, cwd=cwd)
        get_kernel_metrics().increment("node.bun.install")
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}

    async def test(
        self, paths: list[str] | None = None, *, cwd: str | None = None
    ) -> dict[str, Any]:
        require_node_action("bun")
        args = ["test"]
        if paths:
            args += paths
        code, out, err = await self._run(args, cwd=cwd, timeout_s=180.0)
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}


__all__ = ["BunManager", "BunUnavailableError"]
