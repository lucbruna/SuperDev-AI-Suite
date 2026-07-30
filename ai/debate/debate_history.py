from __future__ import annotations

from datetime import datetime
from typing import Any


class DebateHistory:
    """Tracks history of debates and their outcomes."""

    def __init__(self) -> None:
        self._debates: list[dict[str, Any]] = []

    async def record(self, topic: str, agent_count: int, consensus: dict[str, Any]) -> None:
        self._debates.append({
            "topic": topic,
            "agent_count": agent_count,
            "consensus": consensus,
            "timestamp": datetime.now().isoformat(),
        })

    async def summary(self) -> dict[str, Any]:
        if not self._debates:
            return {"total": 0, "avg_agents": 0}
        return {
            "total": len(self._debates),
            "avg_agents": sum(d.get("agent_count", 0) for d in self._debates) / len(self._debates),
            "topics": [d.get("topic") for d in self._debates[-5:]],
        }

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        return await self.summary()
