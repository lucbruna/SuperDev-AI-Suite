from __future__ import annotations

from typing import Any


class DebateMetrics:
    """Metrics collection for debate operations."""

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []

    async def record(self, topic: str, agent_count: int, consensus_reached: bool) -> None:
        self._records.append({
            "topic": topic,
            "agent_count": agent_count,
            "consensus_reached": consensus_reached,
        })

    async def consensus_rate(self) -> float:
        if not self._records:
            return 0.0
        reached = sum(1 for r in self._records if r.get("consensus_reached"))
        return reached / len(self._records)

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "total_debates": len(self._records),
            "consensus_rate": await self.consensus_rate(),
            "avg_agents": sum(r.get("agent_count", 0) for r in self._records) / len(self._records) if self._records else 0,
        }
