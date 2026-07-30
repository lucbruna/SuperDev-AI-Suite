from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any

from .planner_queue import PlannerQueue


class PlannerScheduler:
    """Scheduler for plan execution with timing control."""

    def __init__(self):
        self.queue = PlannerQueue()
        self._scheduled: dict[str, dict[str, Any]] = {}
        self._running = False

    def schedule(self, task_id: str, execute_at: datetime, data: dict[str, Any]) -> None:
        self._scheduled[task_id] = {
            "execute_at": execute_at,
            "data": data,
            "status": "scheduled",
        }

    def cancel(self, task_id: str) -> None:
        if task_id in self._scheduled:
            self._scheduled[task_id]["status"] = "cancelled"

    async def run_pending(self) -> list[str]:
        now = datetime.now(UTC)
        executed: list[str] = []
        for task_id, info in list(self._scheduled.items()):
            if info["status"] == "scheduled" and info["execute_at"] <= now:
                self.queue.enqueue(info["data"])
                info["status"] = "dispatched"
                executed.append(task_id)
        return executed

    def pending_count(self) -> int:
        return sum(1 for v in self._scheduled.values() if v["status"] == "scheduled")
