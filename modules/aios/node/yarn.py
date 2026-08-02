"""yarn package manager wrapper for the AIOS node runtime."""
from __future__ import annotations

from typing import Any

from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.node.node_client import (
    require_node_action,
    run_cli,
)


class YarnUnavailableError(RuntimeError):
    """Raised when the yarn CLI cannot be reached (not installed)."""


class YarnManager:
    """Yarn classic wrapper; degrades when yarn is not installed."""

    def __init__(self, binary: str = "yarn") -> None:
        self.binary = binary

    async def _run(
        self, args: list[str], *, timeout_s: float = 300.0, cwd: str | None = None
    ) -> tuple[int, str, str]:
        return await run_cli(
            self.binary, args, component="yarn", timeout_s=timeout_s, cwd=cwd,
            missing=YarnUnavailableError,
        )

    async def version(self) -> dict[str, Any]:
        require_node_action("yarn")
        code, out, err = await self._run(["--version"], timeout_s=30.0)
        if code != 0:
            raise YarnUnavailableError(
                f"yarn --version failed: {err.strip() or out.strip()}"
            )
        return {"version": out.strip()}

    async def install(
        self, package: str | None = None, *, cwd: str | None = None, dev: bool = False
    ) -> dict[str, Any]:
        require_node_action("yarn")
        if package:
            args = ["add", package]
            if dev:
                args.append("--dev")
        else:
            args = ["install"]
        code, out, err = await self._run(args, cwd=cwd)
        get_kernel_metrics().increment("node.yarn.install")
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}


__all__ = ["YarnManager", "YarnUnavailableError"]
