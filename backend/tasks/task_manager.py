from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Awaitable

from backend.utils.uuid_utils import generate_uuid


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    id: str
    name: str
    func: Callable[..., Awaitable[Any]]
    args: tuple = ()
    kwargs: dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class TaskManager:
    """Simple async task manager."""

    def __init__(self):
        self._tasks: dict[str, Task] = {}

    async def submit(
        self,
        name: str,
        func: Callable[..., Awaitable[Any]],
        args: tuple = (),
        kwargs: dict[str, Any] | None = None,
    ) -> str:
        task_id = generate_uuid()
        task = Task(
            id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs or {},
        )
        self._tasks[task_id] = task
        task.status = TaskStatus.RUNNING
        try:
            task.result = await func(*args, **(kwargs or {}))
            task.status = TaskStatus.COMPLETED
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
        return task_id

    def get_task(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def list_tasks(self, status: TaskStatus | None = None) -> list[Task]:
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return tasks


task_manager = TaskManager()
