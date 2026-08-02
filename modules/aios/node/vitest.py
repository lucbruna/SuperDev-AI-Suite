"""Vitest test runner for the AIOS node runtime."""
from __future__ import annotations

from typing import Any

from modules.aios.node.node_client import (
    require_node_action,
    run_cli,
)


class VitestUnavailableError(RuntimeError):
    """Raised when vitest cannot be reached (not installed in the project)."""


class VitestRunner:
    """Runs vitest through npx against the project-local installation."""

    def __init__(self, binary: str = "npx") -> None:
        self.binary = binary

    async def _run(
        self, args: list[str], *, timeout_s: float = 300.0, cwd: str | None = None
    ) -> tuple[int, str, str]:
        return await run_cli(
            self.binary, args, component="vitest", timeout_s=timeout_s, cwd=cwd,
            missing=VitestUnavailableError,
        )

    async def version(self, *, cwd: str | None = None) -> dict[str, Any]:
        require_node_action("vitest")
        code, out, err = await self._run(
            ["--no-install", "vitest", "--version"], timeout_s=60.0, cwd=cwd
        )
        if code != 0:
            raise VitestUnavailableError(
                f"vitest not installed: {err.strip() or out.strip()}"
            )
        return {"version": out.strip().splitlines()[-1]}

    async def run(
        self, paths: list[str] | None = None, *, cwd: str | None = None
    ) -> dict[str, Any]:
        require_node_action("vitest")
        args = ["--no-install", "vitest", "run"]
        if paths:
            args += paths
        code, out, err = await self._run(args, cwd=cwd, timeout_s=300.0)
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}


__all__ = ["VitestRunner", "VitestUnavailableError"]
