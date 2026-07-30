from __future__ import annotations

from enum import IntEnum
from typing import Any


class PriorityLevel(IntEnum):
    LOWEST = -2
    LOW = -1
    NORMAL = 0
    HIGH = 1
    HIGHEST = 2


class PlannerPriority:
    """Priority management for planner tasks."""

    def __init__(self):
        self._priorities: dict[str, PriorityLevel] = {}

    def set_priority(self, task_id: str, level: PriorityLevel | int) -> None:
        self._priorities[task_id] = PriorityLevel(level) if isinstance(level, int) else level

    def get_priority(self, task_id: str) -> PriorityLevel:
        return self._priorities.get(task_id, PriorityLevel.NORMAL)

    def remove(self, task_id: str) -> None:
        self._priorities.pop(task_id, None)

    def sorted_tasks(self, tasks: list[Any]) -> list[Any]:
        return sorted(tasks, key=lambda t: self.get_priority(getattr(t, "id", "")), reverse=True)
