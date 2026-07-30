from __future__ import annotations

import logging
from typing import Any


class TaskScheduler:
    """Schedules and manages code execution tasks."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.execution.scheduler")
        self._queue: list[dict[str, Any]] = []

    def enqueue(self, task: dict[str, Any]) -> None:
        self._queue.append(task)
        self._log.info("Enqueued task %s", task.get("id", "?"))

    def dequeue(self) -> dict[str, Any] | None:
        return self._queue.pop(0) if self._queue else None

    @property
    def pending(self) -> int:
        return len(self._queue)
