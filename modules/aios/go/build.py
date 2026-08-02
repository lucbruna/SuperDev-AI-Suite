"""Go build — go build wrapper (Vol 12, Fase 20)."""
from __future__ import annotations

from typing import Any

from modules.aios.go.go_client import (
    GoClient,
    require_go_action,
)


class GoBuild:
    """Builds go packages/binaries."""

    def __init__(self, client: GoClient) -> None:
        self._client = client

    async def build(
        self,
        *,
        cwd: str | None = None,
        output: str | None = None,
        packages: list[str] | None = None,
    ) -> dict[str, Any]:
        require_go_action("build")
        args = ["build"]
        if output:
            args += ["-o", output]
        if packages:
            args += packages
        code, out, err = await self._client._run(args, cwd=cwd, timeout_s=600.0)
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}

    async def vet(self, *, cwd: str | None = None) -> dict[str, Any]:
        require_go_action("build")
        code, out, err = await self._client._run(["vet", "./..."], cwd=cwd, timeout_s=300.0)
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}


__all__ = ["GoBuild"]
