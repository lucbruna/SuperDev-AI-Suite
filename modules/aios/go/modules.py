"""Go module management — go mod / go list / go get (Vol 12, Fase 20)."""
from __future__ import annotations

from typing import Any

from modules.aios.go.go_client import (
    GoClient,
    GoUnavailableError,
    require_go_action,
)


class GoModules:
    """Manages go.mod: list, tidy and add module dependencies."""

    def __init__(self, client: GoClient) -> None:
        self._client = client

    async def list(self, *, cwd: str | None = None) -> dict[str, Any]:
        require_go_action("modules")
        code, out, err = await self._client._run(["list", "-m", "all"], cwd=cwd, timeout_s=120.0)
        if code != 0:
            raise GoUnavailableError(f"go list failed: {err.strip() or out.strip()}")
        return {"modules": [line.strip() for line in out.splitlines() if line.strip()]}

    async def add(self, module: str, *, cwd: str | None = None) -> dict[str, Any]:
        require_go_action("modules")
        code, out, err = await self._client._run(["get", module], cwd=cwd, timeout_s=300.0)
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}

    async def tidy(self, *, cwd: str | None = None) -> dict[str, Any]:
        require_go_action("modules")
        code, out, err = await self._client._run(["mod", "tidy"], cwd=cwd, timeout_s=300.0)
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}


__all__ = ["GoModules"]
