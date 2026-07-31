from __future__ import annotations

from datetime import datetime
from typing import Any


class ChainHistory:
    """Tracks history of reasoning chain executions."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    async def record(self, chain: dict[str, Any], outcome: str) -> None:
        self._entries.append(
            {
                "steps": len(chain.get("steps", [])),
                "outcome": outcome,
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def summary(self) -> dict[str, Any]:
        if not self._entries:
            return {"total": 0, "successful": 0, "failed": 0}
        return {
            "total": len(self._entries),
            "successful": sum(1 for e in self._entries if e.get("outcome") == "success"),
            "failed": sum(1 for e in self._entries if e.get("outcome") == "failed"),
        }

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        return await self.summary()
