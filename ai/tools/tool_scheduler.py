from __future__ import annotations

import time
import uuid
from typing import Any


class ScheduledTask:
    """Represents a scheduled tool execution."""

    def __init__(self, task_id: str, tool_name: str, params: dict[str, Any],
                 interval: float, repeat: bool = False) -> None:
        self.task_id = task_id
        self.tool_name = tool_name
        self.params = params
        self.interval = interval
        self.repeat = repeat
        self.next_run: float = time.time() + interval
        self.runs: int = 0
        self.cancelled: bool = False


class ToolScheduler:
    """Schedules tool executions at intervals."""

    def __init__(self) -> None:
        self._tasks: dict[str, ScheduledTask] = {}
        self._results: dict[str, list[dict[str, Any]]] = {}

    def schedule(self, tool_name: str, params: dict[str, Any],
                 interval: float, repeat: bool = False) -> str:
        task_id = str(uuid.uuid4())
        task = ScheduledTask(task_id, tool_name, params, interval, repeat)
        self._tasks[task_id] = task
        return task_id

    def cancel(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if task:
            task.cancelled = True
            return True
        return False

    def get_task(self, task_id: str) -> ScheduledTask | None:
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[ScheduledTask]:
        return [t for t in self._tasks.values() if not t.cancelled]

    @property
    def task_count(self) -> int:
        return len(self.list_tasks())

    def get_pending(self) -> list[ScheduledTask]:
        now = time.time()
        return [t for t in self.list_tasks() if t.next_run <= now]

    def record_result(self, task_id: str, result: dict[str, Any]) -> None:
        if task_id not in self._results:
            self._results[task_id] = []
        self._results[task_id].append(result)

    def get_results(self, task_id: str) -> list[dict[str, Any]]:
        return self._results.get(task_id, [])

    def to_dict(self) -> dict[str, Any]:
        return {
            "active_tasks": self.task_count,
            "tasks": {t.task_id: {"tool": t.tool_name, "interval": t.interval, "repeat": t.repeat}
                      for t in self.list_tasks()},
        }
