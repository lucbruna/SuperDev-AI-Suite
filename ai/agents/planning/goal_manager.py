"""Goal management for planning subsystem."""
from __future__ import annotations

import time
import uuid
from typing import Any


class GoalManager:
    """Manages goals with priorities, dependencies, and status tracking."""

    def __init__(self) -> None:
        self._goals: dict[str, dict[str, Any]] = {}

    def add_goal(self, description: str,
                 context: dict[str, Any] | None = None,
                 priority: int = 5,
                 parent_id: str | None = None) -> dict[str, Any]:
        goal_id = f"goal_{uuid.uuid4().hex[:12]}"
        goal = {
            "goal_id": goal_id,
            "description": description,
            "context": context or {},
            "priority": priority,
            "parent_id": parent_id,
            "status": "active",
            "created_at": time.time(),
            "sub_goals": [],
            "progress": 0.0,
        }
        self._goals[goal_id] = goal
        if parent_id and parent_id in self._goals:
            self._goals[parent_id]["sub_goals"].append(goal_id)
        return goal

    def update_goal(self, goal_id: str, **kwargs: Any) -> bool:
        goal = self._goals.get(goal_id)
        if goal is None:
            return False
        for key, value in kwargs.items():
            if key in goal:
                goal[key] = value
        goal["updated_at"] = time.time()
        return True

    def complete_goal(self, goal_id: str) -> bool:
        return self.update_goal(goal_id, status="completed", progress=1.0)

    def fail_goal(self, goal_id: str, reason: str = "") -> bool:
        return self.update_goal(goal_id, status="failed", failure_reason=reason)

    def get_goal(self, goal_id: str) -> dict[str, Any] | None:
        return self._goals.get(goal_id)

    def get_active_goals(self) -> list[dict[str, Any]]:
        return [g for g in self._goals.values() if g["status"] == "active"]

    def get_by_priority(self, min_priority: int = 0) -> list[dict[str, Any]]:
        return sorted(
            [g for g in self._goals.values() if g["priority"] >= min_priority],
            key=lambda g: g["priority"], reverse=True,
        )

    def remove_goal(self, goal_id: str) -> bool:
        return self._goals.pop(goal_id, None) is not None

    def count(self) -> int:
        return len(self._goals)

    def snapshot(self) -> dict[str, Any]:
        return {
            "total": len(self._goals),
            "active": len(self.get_active_goals()),
            "goals": list(self._goals.keys()),
        }
