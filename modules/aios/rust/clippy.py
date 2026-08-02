"""clippy linter wrapper for the AIOS rust runtime (Vol 12, Fase 21)."""
from __future__ import annotations

from typing import Any

from modules.aios.rust.rust_client import (
    CargoClient,
    require_rust_action,
)


class Clippy:
    """Runs cargo clippy (lints) over the workspace."""

    def __init__(self, client: CargoClient) -> None:
        self._client = client

    async def run(
        self,
        *,
        cwd: str | None = None,
        warnings_as_errors: bool = False,
        all_targets: bool = True,
    ) -> dict[str, Any]:
        require_rust_action("clippy")
        args = ["clippy"]
        if warnings_as_errors:
            args.append("--")
            args.append("-D")
            args.append("warnings")
        if all_targets:
            args.append("--all-targets")
        code, out, err = await self._client._run(args, cwd=cwd)
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}


__all__ = ["Clippy"]
