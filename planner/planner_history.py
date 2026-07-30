from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class PlannerHistory:
    """History tracking for plans and executions."""

    def __init__(self):
        self._entries: list[dict[str, Any]] = []
        self._max_entries: int = 10000

    def record(self, plan_id: str, action: str, data: dict[str, Any] | None = None) -> None:
        self._entries.append({
            "plan_id": plan_id,
            "action": action,
            "data": data or {},
            "timestamp": datetime.now(UTC).isoformat(),
        })
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries:]

    def get_history(self, plan_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        entries = self._entries
        if plan_id:
            entries = [e for e in entries if e["plan_id"] == plan_id]
        return entries[-limit:]

    def clear(self) -> None:
        self._entries.clear()
