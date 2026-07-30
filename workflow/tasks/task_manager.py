from __future__ import annotations

import time
from typing import Any

from .task import Task, TaskStatus


class TaskManager:
    """Manages task lifecycle and storage."""

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    def create(self, name: str, action: str, params: dict[str, Any] | None = None) -> Task:
        task_id = f"task_{int(time.time() * 1000)}"
        task = Task(
            id=task_id,
            name=name,
            action=action,
            params=params or {},
        )
        self._tasks[task_id] = task
        return task

    def get(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def update_status(self, task_id: str, status: TaskStatus) -> None:
        task = self._tasks.get(task_id)
        if task:
            task.status = status
            task.updated_at = time.time()

    def list_by_status(self, status: TaskStatus) -> list[Task]:
        return [t for t in self._tasks.values() if t.status == status]

    def count(self) -> int:
        return len(self._tasks)

    def clear_completed(self) -> int:
        completed = [t for t in self._tasks.values() if t.status == TaskStatus.COMPLETED]
        for t in completed:
            del self._tasks[t.id]
        return len(completed)
