"""Task scheduling with dependency resolution and priority ordering."""

from __future__ import annotations

import time
from typing import Any


class Scheduler:
    """Schedules tasks with dependency resolution and priority-based ordering."""

    def __init__(self) -> None:
        self._scheduled_count: int = 0

    def schedule(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        ordered = self._topological_sort(tasks)
        for i, task in enumerate(ordered):
            task["schedule_order"] = i
            task["scheduled_at"] = time.time()
        self._scheduled_count += len(ordered)
        return ordered

    def _topological_sort(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        task_map = {t.get("title", t.get("task_id", "")): t for t in tasks}
        visited: set[str] = set()
        result: list[dict[str, Any]] = []

        def _visit(title: str) -> None:
            if title in visited:
                return
            visited.add(title)
            task = task_map.get(title)
            if task is None:
                return
            for dep in task.get("dependencies", []):
                _visit(dep)
            result.append(task)

        for task in tasks:
            _visit(task.get("title", task.get("task_id", "")))

        remaining = [t for t in tasks if t not in result]
        result.extend(remaining)
        return result

    def get_next(self, tasks: list[dict[str, Any]], completed: list[str]) -> dict[str, Any] | None:
        for task in tasks:
            if task.get("status") != "pending":
                continue
            deps = task.get("dependencies", [])
            if all(d in completed for d in deps):
                return task
        return None

    def snapshot(self) -> dict[str, Any]:
        return {"total_scheduled": self._scheduled_count}
