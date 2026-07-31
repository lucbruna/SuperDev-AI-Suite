"""Task lifecycle management."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_models import (ProjectRecord, TaskPriority,
                                                TaskRecord, TaskStatus)
from collaboration.collaboration_protocols import new_id
from collaboration.tasks.task_activity import TaskActivityLog
from collaboration.tasks.task_dependencies import TaskDependencies
from collaboration.tasks.task_scheduler import TaskScheduler
from collaboration.tasks.task_status import can_transition, transition


class TaskManager:
    """CRUD for tasks plus dependencies, scheduler and activity."""

    def __init__(self, registry: Any = None) -> None:
        self.registry = registry
        self.dependencies = TaskDependencies()
        self.scheduler = TaskScheduler()
        self.activity_log = TaskActivityLog()
        self._order: dict[str, int] = {}
        self._next_order = 0

    def create(self, project_id: str, workspace_id: str, title: str,
               description: str = "",
               priority: TaskPriority = TaskPriority.MEDIUM,
               assignee_id: str = "",
               status: TaskStatus = TaskStatus.TODO,
               **extra: Any) -> TaskRecord:
        self._next_order += 1
        task = TaskRecord(task_id=new_id("task"), project_id=project_id,
                          workspace_id=workspace_id, title=title,
                          description=description, priority=priority,
                          assignee_id=assignee_id, status=status,
                          **extra)
        if self.registry is not None:
            self.registry.register_task(task.task_id, task)
        self._order[task.task_id] = self._next_order
        return task

    def get(self, task_id: str) -> TaskRecord | None:
        if self.registry is None:
            return None
        return self.registry.get_task(task_id)

    def list(self) -> list[str]:
        if self.registry is None:
            return []
        return self.registry.list_tasks()

    def remove(self, task_id: str) -> bool:
        self.dependencies.remove(task_id)
        self._order.pop(task_id, None)
        if self.registry is not None:
            return self.registry.remove_task(task_id)
        return False

    def by_project(self, project_id: str) -> list[TaskRecord]:
        if self.registry is None:
            return []
        tasks = []
        for task_id in self.registry.list_tasks():
            task = self.registry.get_task(task_id)
            if task is not None and task.project_id == project_id:
                tasks.append(task)
        return tasks

    def ordered(self) -> list[TaskRecord]:
        tasks = self.by_project_ordered()
        return sorted(tasks, key=lambda t: self._order.get(t.task_id, 0))

    def by_project_ordered(self) -> list[TaskRecord]:
        if self.registry is None:
            return []
        tasks = []
        for task_id in self.registry.list_tasks():
            task = self.registry.get_task(task_id)
            if task is not None:
                tasks.append(task)
        return sorted(tasks, key=lambda t: self._order.get(t.task_id, 0))

    def set_status(self, task_id: str, status: TaskStatus,
                   force: bool = False) -> TaskRecord | None:
        task = self.get(task_id)
        if task is None:
            return None
        if force or can_transition(task.status, status):
            task.status = transition(task.status, status)
        return task

    def set_assignee(self, task_id: str, assignee_id: str) -> TaskRecord | None:
        task = self.get(task_id)
        if task is None:
            return None
        task.assignee_id = assignee_id
        return task

    def count(self) -> int:
        return len(self._order)
