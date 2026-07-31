from __future__ import annotations

from collections.abc import Callable
from typing import Any


class ReusableTask:
    """A reusable task definition."""

    def __init__(self, task_id: str, name: str, category: str, handler: Callable | None = None, description: str = ""):
        self._task_id = task_id
        self._name = name
        self._category = category
        self._handler = handler
        self._description = description
        self._parameters: dict[str, Any] = {}

    @property
    def task_id(self) -> str:
        return self._task_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def category(self) -> str:
        return self._category

    @property
    def handler(self) -> Callable | None:
        return self._handler

    @handler.setter
    def handler(self, value: Callable | None) -> None:
        self._handler = value

    @property
    def description(self) -> str:
        return self._description

    @property
    def parameters(self) -> dict[str, Any]:
        return dict(self._parameters)

    def add_parameter(self, name: str, default: Any = None) -> None:
        self._parameters[name] = default

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self._task_id,
            "name": self._name,
            "category": self._category,
            "description": self._description,
            "parameters": dict(self._parameters),
        }


class ReusableTasks:
    """Registry of reusable task definitions."""

    def __init__(self):
        self._tasks: dict[str, ReusableTask] = {}

    @property
    def count(self) -> int:
        return len(self._tasks)

    def add(self, task: ReusableTask) -> None:
        self._tasks[task.task_id] = task

    def get(self, task_id: str) -> ReusableTask | None:
        return self._tasks.get(task_id)

    def get_by_category(self, category: str) -> list[ReusableTask]:
        return [t for t in self._tasks.values() if t.category == category]

    def execute(self, task_id: str, **kwargs: Any) -> Any | None:
        task = self._tasks.get(task_id)
        if task is None or task.handler is None:
            return None
        return task.handler(**kwargs)

    def remove(self, task_id: str) -> bool:
        return self._tasks.pop(task_id, None) is not None

    def clear(self) -> None:
        self._tasks.clear()
