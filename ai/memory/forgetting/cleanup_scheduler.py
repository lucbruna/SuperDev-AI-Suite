from __future__ import annotations

import time
from collections.abc import Callable


class CleanupTask:
    """A scheduled cleanup task."""

    def __init__(self, task_id: str, interval: float, action: Callable[[], None]):
        self._task_id = task_id
        self._interval = interval
        self._action = action
        self._last_run: float = 0.0
        self._run_count: int = 0

    @property
    def task_id(self) -> str:
        return self._task_id

    @property
    def interval(self) -> float:
        return self._interval

    @property
    def last_run(self) -> float:
        return self._last_run

    @property
    def run_count(self) -> int:
        return self._run_count

    def is_due(self) -> bool:
        return time.time() - self._last_run >= self._interval

    def execute(self) -> None:
        self._action()
        self._last_run = time.time()
        self._run_count += 1


class CleanupScheduler:
    """Schedules and runs periodic cleanup tasks."""

    def __init__(self):
        self._tasks: dict[str, CleanupTask] = {}

    @property
    def task_count(self) -> int:
        return len(self._tasks)

    def schedule(self, task_id: str, interval: float, action: Callable[[], None]) -> CleanupTask:
        task = CleanupTask(task_id, interval, action)
        self._tasks[task_id] = task
        return task

    def unschedule(self, task_id: str) -> bool:
        return self._tasks.pop(task_id, None) is not None

    def run_due(self) -> int:
        count = 0
        for task in list(self._tasks.values()):
            if task.is_due():
                task.execute()
                count += 1
        return count

    def run_all(self) -> int:
        count = 0
        for task in list(self._tasks.values()):
            task.execute()
            count += 1
        return count

    def get_task(self, task_id: str) -> CleanupTask | None:
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[str]:
        return list(self._tasks.keys())

    def clear(self) -> None:
        self._tasks.clear()
