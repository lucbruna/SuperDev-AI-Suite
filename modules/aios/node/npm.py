"""npm package manager wrapper for the AIOS node runtime."""
from __future__ import annotations

import json
from typing import Any

from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.node.node_client import (
    require_node_action,
    run_cli,
)


class NpmUnavailableError(RuntimeError):
    """Raised when the npm CLI cannot be reached."""


class NpmManager:
    """Installs, removes and inspects packages with the npm CLI."""

    def __init__(self, binary: str = "npm") -> None:
        self.binary = binary

    async def _run(
        self, args: list[str], *, timeout_s: float = 300.0, cwd: str | None = None
    ) -> tuple[int, str, str]:
        return await run_cli(
            self.binary, args, component="npm", timeout_s=timeout_s, cwd=cwd,
            missing=NpmUnavailableError,
        )

    async def version(self) -> dict[str, Any]:
        require_node_action("npm")
        code, out, err = await self._run(["--version"], timeout_s=30.0)
        if code != 0:
            raise NpmUnavailableError(
                f"npm --version failed: {err.strip() or out.strip()}"
            )
        return {"version": out.strip()}

    async def install(
        self,
        package: str | None = None,
        *,
        cwd: str | None = None,
        dev: bool = False,
        global_: bool = False,
    ) -> dict[str, Any]:
        require_node_action("npm")
        args = ["install"]
        if dev:
            args.append("--save-dev")
        if global_:
            args.append("--global")
        if package:
            args.append(package)
        args += ["--no-audit", "--no-fund"]
        code, out, err = await self._run(args, cwd=cwd)
        get_kernel_metrics().increment("node.npm.install")
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}

    async def uninstall(
        self, package: str, *, cwd: str | None = None, global_: bool = False
    ) -> dict[str, Any]:
        require_node_action("npm")
        args = ["uninstall", package]
        if global_:
            args.append("--global")
        code, out, err = await self._run(args, cwd=cwd)
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}

    async def run_script(self, name: str, *, cwd: str | None = None) -> dict[str, Any]:
        require_node_action("npm")
        code, out, err = await self._run(["run", name], cwd=cwd)
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}

    async def list(self, *, cwd: str | None = None) -> list[dict[str, Any]]:
        require_node_action("npm")
        code, out, err = await self._run(
            ["list", "--json", "--depth=0"], cwd=cwd, timeout_s=60.0
        )
        if code != 0:
            return []
        try:
            data = json.loads(out)
        except json.JSONDecodeError:
            return []
        deps: dict[str, Any] = data.get("dependencies", {})
        return [
            {"name": name, "version": spec.get("version", "")}
            for name, spec in deps.items()
            if isinstance(spec, dict)
        ]


__all__ = ["NpmManager", "NpmUnavailableError"]
