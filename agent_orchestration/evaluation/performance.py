"""Performance tracking per agent (Volume 31)."""

from __future__ import annotations

from typing import Any


class PerformanceTracker:
    """Tracks execution duration and outcome counts per agent."""

    def __init__(self) -> None:
        self._records: dict[str, list[dict[str, Any]]] = {}

    def record(self, agent_id: str, duration: float, success: bool) -> None:
        self._records.setdefault(agent_id, []).append(
            {"duration": duration, "success": success})

    def count(self, agent_id: str | None = None) -> int:
        if agent_id is None:
            return sum(len(records) for records in self._records.values())
        return len(self._records.get(agent_id, []))

    def average_time(self, agent_id: str) -> float:
        records = self._records.get(agent_id, [])
        if not records:
            return 0.0
        return sum(record["duration"] for record in records) / len(records)

    def successes(self, agent_id: str) -> int:
        return sum(1 for record in self._records.get(agent_id, [])
                   if record["success"])

    def errors(self, agent_id: str) -> int:
        return sum(1 for record in self._records.get(agent_id, [])
                   if not record["success"])

    def summary(self, agent_id: str) -> dict[str, Any]:
        return {"count": self.count(agent_id),
                "successes": self.successes(agent_id),
                "errors": self.errors(agent_id),
                "average_time": self.average_time(agent_id)}
