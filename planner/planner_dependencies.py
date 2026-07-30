from __future__ import annotations

from typing import Any


class PlannerDependencies:
    """Dependency resolution for planner tasks."""

    def __init__(self):
        self._dependencies: dict[str, list[str]] = {}

    def add_dependency(self, task_id: str, depends_on: str) -> None:
        if task_id not in self._dependencies:
            self._dependencies[task_id] = []
        self._dependencies[task_id].append(depends_on)

    def get_dependencies(self, task_id: str) -> list[str]:
        return self._dependencies.get(task_id, [])

    def get_dependents(self, task_id: str) -> list[str]:
        return [tid for tid, deps in self._dependencies.items() if task_id in deps]

    def is_ready(self, task_id: str, completed: set[str]) -> bool:
        return all(dep in completed for dep in self.get_dependencies(task_id))

    def ready_tasks(self, completed: set[str]) -> list[str]:
        return [
            tid for tid in self._dependencies
            if tid not in completed and self.is_ready(tid, completed)
        ]

    def clear(self) -> None:
        self._dependencies.clear()
