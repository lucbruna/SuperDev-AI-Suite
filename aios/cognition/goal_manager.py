"""AIOS Goal Manager — goal registration, priority and tracking.

Goals have id, description, priority and status; the manager orders
them by priority and tracks completion.
"""

from __future__ import annotations

import time
import uuid
from typing import Any

STATUS_PENDING = "pending"
STATUS_IN_PROGRESS = "in_progress"
STATUS_COMPLETED = "completed"
STATUS_BLOCKED = "blocked"


class GoalManager:
    """Track and prioritize goals."""

    def __init__(self) -> None:
        self._goals: dict[str, dict[str, Any]] = {}

    def add(self, description: str, priority: int = 5, **meta: Any) -> str:
        goal_id = f"goal-{uuid.uuid4().hex[:10]}"
        self._goals[goal_id] = {
            "goal_id": goal_id,
            "description": description,
            "priority": int(priority),
            "status": STATUS_PENDING,
            "created_at": time.time(),
            **meta,
        }
        return goal_id

    def set_status(self, goal_id: str, status: str) -> bool:
        goal = self._goals.get(goal_id)
        if goal is None:
            return False
        goal["status"] = status
        return True

    def priorities(self) -> list[dict[str, Any]]:
        """Return goals ordered by priority (desc) then creation."""
        return sorted(
            self._goals.values(),
            key=lambda g: (-g["priority"], g["created_at"]),
        )

    def by_status(self, status: str) -> list[dict[str, Any]]:
        return [g for g in self._goals.values() if g["status"] == status]

    def stats(self) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for goal in self._goals.values():
            counts[goal["status"]] = counts.get(goal["status"], 0) + 1
        return {"total": len(self._goals), **counts}
