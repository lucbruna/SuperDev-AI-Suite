from __future__ import annotations

from typing import Any


class DependencyManager:
    """Manages task dependencies."""

    def __init__(self) -> None:
        self._dependencies: dict[str, list[str]] = {}

    def add_dependency(self, task_id: str, depends_on: str) -> None:
        if task_id not in self._dependencies:
            self._dependencies[task_id] = []
        self._dependencies[task_id].append(depends_on)

    def get_dependencies(self, task_id: str) -> list[str]:
        return list(self._dependencies.get(task_id, []))

    def is_ready(self, task_id: str, completed: list[str]) -> bool:
        deps = self.get_dependencies(task_id)
        return all(d in completed for d in deps)

    def remove(self, task_id: str) -> bool:
        return self._dependencies.pop(task_id, None) is not None

    def clear(self) -> None:
        self._dependencies.clear()

    def to_dict(self) -> dict[str, Any]:
        return dict(self._dependencies)
