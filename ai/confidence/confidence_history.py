from __future__ import annotations

from datetime import datetime
from typing import Any


class ConfidenceHistory:
    """Tracks history of confidence scores over time."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    async def record(self, score: float, context_id: str) -> None:
        self._entries.append({
            "score": score,
            "context_id": context_id,
            "timestamp": datetime.now().isoformat(),
        })

    async def get_trend(self, context_id: str) -> list[dict[str, Any]]:
        return [e for e in self._entries if e.get("context_id") == context_id]

    async def summary(self) -> dict[str, Any]:
        if not self._entries:
            return {"min": 0.0, "max": 0.0, "avg": 0.0, "count": 0}
        scores = [e.get("score", 0) for e in self._entries]
        return {"min": min(scores), "max": max(scores), "avg": sum(scores) / len(scores), "count": len(scores)}

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        return await self.summary()
