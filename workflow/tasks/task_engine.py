from __future__ import annotations

import logging
from typing import Any

from .task import Task
from .task_manager import TaskManager
from .task_queue import TaskQueue
from .task_executor import TaskExecutor


class TaskEngine:
    """Central engine for task creation and execution."""

    def __init__(self) -> None:
        self._manager = TaskManager()
        self._queue = TaskQueue()
        self._executor = TaskExecutor()
        self._log = logging.getLogger("superdev.workflow.tasks.engine")

    def create_task(self, name: str, action: str, params: dict[str, Any] | None = None) -> Task:
        task = self._manager.create(name, action, params)
        self._queue.enqueue(task)
        return task

    def execute_next(self) -> Task | None:
        task = self._queue.dequeue()
        if task:
            self._executor.execute(task)
        return task

    def get_status(self, task_id: str) -> str | None:
        task = self._manager.get(task_id)
        return task.status if task else None

    @property
    def manager(self) -> TaskManager:
        return self._manager

    @property
    def queue(self) -> TaskQueue:
        return self._queue
