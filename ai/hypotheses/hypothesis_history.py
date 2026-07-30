from __future__ import annotations

from datetime import datetime
from typing import Any


class HypothesisHistory:
    """Tracks history of hypotheses and their outcomes."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    async def record(self, hypothesis: dict[str, Any], outcome: str) -> None:
        self._entries.append({
            **hypothesis,
            "outcome": outcome,
            "timestamp": datetime.now().isoformat(),
        })

    async def get_history(self, hypothesis_id: str) -> list[dict[str, Any]]:
        return [e for e in self._entries if e.get("id") == hypothesis_id]

    async def summary(self) -> dict[str, Any]:
        return {
            "total": len(self._entries),
            "confirmed": sum(1 for e in self._entries if e.get("outcome") == "confirmed"),
            "rejected": sum(1 for e in self._entries if e.get("outcome") == "rejected"),
        }

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        return await self.summary()
