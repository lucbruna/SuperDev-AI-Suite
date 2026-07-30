from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class PlannerState:
    """Manages planner execution state."""

    def __init__(self):
        self._plans: dict[str, Any] = {}
        self._tasks: dict[str, Any] = {}
        self._executions: dict[str, Any] = {}

    def set_plan_state(self, plan_id: str, state: dict[str, Any]) -> None:
        self._plans[plan_id] = {**state, "updated_at": datetime.now(UTC).isoformat()}

    def get_plan_state(self, plan_id: str) -> dict[str, Any] | None:
        return self._plans.get(plan_id)

    def set_task_state(self, task_id: str, state: dict[str, Any]) -> None:
        self._tasks[task_id] = {**state, "updated_at": datetime.now(UTC).isoformat()}

    def get_task_state(self, task_id: str) -> dict[str, Any] | None:
        return self._tasks.get(task_id)

    def set_execution_state(self, execution_id: str, state: dict[str, Any]) -> None:
        self._executions[execution_id] = {**state, "updated_at": datetime.now(UTC).isoformat()}

    def get_execution_state(self, execution_id: str) -> dict[str, Any] | None:
        return self._executions.get(execution_id)

    def snapshot(self) -> dict[str, Any]:
        return {
            "plans": len(self._plans),
            "tasks": len(self._tasks),
            "executions": len(self._executions),
            "timestamp": datetime.now(UTC).isoformat(),
        }
