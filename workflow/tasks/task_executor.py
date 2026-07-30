from __future__ import annotations

import logging
from typing import Any, Callable

from .task import Task, TaskStatus


class TaskExecutor:
    """Executes tasks by invoking registered actions."""

    def __init__(self) -> None:
        self._actions: dict[str, Callable[..., Any]] = {}
        self._log = logging.getLogger("superdev.workflow.tasks.executor")

    def register(self, name: str, fn: Callable[..., Any]) -> None:
        self._actions[name] = fn

    def execute(self, task: Task) -> Any:
        fn = self._actions.get(task.action)
        if not fn:
            task.status = TaskStatus.FAILED
            task.error = f"Unknown action: {task.action}"
            return None
        task.status = TaskStatus.RUNNING
        try:
            result = fn(**task.params)
            task.status = TaskStatus.COMPLETED
            task.result = result
            return result
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            raise
