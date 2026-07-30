from __future__ import annotations

import logging
import uuid
from enum import Enum
from typing import Any


class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class Task:
    """Represents a project task."""

    def __init__(self, title: str, project_id: str) -> None:
        self.id = str(uuid.uuid4())
        self.title = title
        self.project_id = project_id
        self.status = TaskStatus.TODO
        self.assignee: str | None = None
        self.priority: str = "medium"


class TaskManager:
    """Manages project tasks."""

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}
        self._log = logging.getLogger("superdev.project.tasks")

    def create(self, title: str, project_id: str) -> Task:
        task = Task(title=title, project_id=project_id)
        self._tasks[task.id] = task
        self._log.info("Created task %s", task.id)
        return task

    def get(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def list_by_project(self, project_id: str) -> list[Task]:
        return [t for t in self._tasks.values() if t.project_id == project_id]

    def assign(self, task_id: str, user: str) -> None:
        task = self._tasks.get(task_id)
        if task:
            task.assignee = user

    def update_status(self, task_id: str, status: TaskStatus) -> None:
        task = self._tasks.get(task_id)
        if task:
            task.status = status
