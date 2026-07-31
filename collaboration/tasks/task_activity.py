"""Task activity tracking."""

from __future__ import annotations

import time
from typing import Any


class TaskActivity:
    """Records events on a task."""

    def __init__(self, task_id: str, max_entries: int = 200) -> None:
        self.task_id = task_id
        self.max_entries = max_entries
        self._entries: list[dict[str, Any]] = []

    def record(self, action: str, actor_id: str,
               details: dict[str, Any] | None = None) -> dict[str, Any]:
        entry = {"action": action, "actor_id": actor_id,
                 "details": dict(details or {}), "timestamp": time.time()}
        self._entries.append(entry)
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries:]
        return entry

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(self._entries[-limit:])

    def count(self) -> int:
        return len(self._entries)


class TaskActivityLog:
    """Registry of task activity per task."""

    def __init__(self) -> None:
        self._logs: dict[str, TaskActivity] = {}

    def for_task(self, task_id: str) -> TaskActivity:
        log = self._logs.get(task_id)
        if log is None:
            log = TaskActivity(task_id)
            self._logs[task_id] = log
        return log
