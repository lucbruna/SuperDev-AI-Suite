from __future__ import annotations

from typing import Any

from .task import Task


class TaskDependency:
    """Manages task dependency resolution."""

    def __init__(self) -> None:
        self._dependencies: dict[str, list[str]] = {}

    def add_dependency(self, task_id: str, depends_on: str) -> None:
        if task_id not in self._dependencies:
            self._dependencies[task_id] = []
        self._dependencies[task_id].append(depends_on)

    def get_dependencies(self, task_id: str) -> list[str]:
        return self._dependencies.get(task_id, [])

    def is_ready(self, task: Task, completed: set[str]) -> bool:
        deps = self._dependencies.get(task.id, []) + task.depends_on
        return all(dep in completed for dep in deps)

    def topological_sort(self, tasks: list[Task]) -> list[Task]:
        visited: set[str] = set()
        result: list[Task] = []
        task_map = {t.id: t for t in tasks}

        def visit(task_id: str) -> None:
            if task_id in visited:
                return
            visited.add(task_id)
            for dep in self._dependencies.get(task_id, []):
                if dep in task_map:
                    visit(dep)
            if task_id in task_map:
                result.append(task_map[task_id])

        for task in tasks:
            visit(task.id)
        return result
