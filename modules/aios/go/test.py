"""Go test — go test wrapper (Vol 12, Fase 20)."""
from __future__ import annotations

from typing import Any

from modules.aios.go.go_client import (
    GoClient,
    require_go_action,
)


class GoTest:
    """Runs go tests (defaults to ./...)."""

    def __init__(self, client: GoClient) -> None:
        self._client = client

    async def run(
        self,
        *,
        cwd: str | None = None,
        packages: list[str] | None = None,
        verbose: bool = False,
    ) -> dict[str, Any]:
        require_go_action("test")
        args = ["test"]
        if verbose:
            args.append("-v")
        args += packages or ["./..."]
        code, out, err = await self._client._run(args, cwd=cwd, timeout_s=600.0)
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}


__all__ = ["GoTest"]
