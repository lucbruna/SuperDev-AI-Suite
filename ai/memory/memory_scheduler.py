from __future__ import annotations

import asyncio
import time
from collections.abc import Callable
from typing import Any


class ScheduledTask:
    """A single scheduled task in the memory scheduler."""

    def __init__(
        self,
        name: str,
        interval: float,
        callback: Callable[[], None],
        run_immediately: bool = False,
    ):
        self._name = name
        self._interval = interval
        self._callback = callback
        self._last_run: float = 0.0
        self._run_count: int = 0
        self._enabled: bool = True
        if run_immediately:
            self._last_run = -interval

    @property
    def name(self) -> str:
        return self._name

    @property
    def interval(self) -> float:
        return self._interval

    @property
    def last_run(self) -> float:
        return self._last_run

    @property
    def run_count(self) -> int:
        return self._run_count

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def is_due(self) -> bool:
        return self._enabled and (time.time() - self._last_run >= self._interval)

    async def execute(self) -> None:
        if not self._enabled:
            return
        self._callback()
        self._last_run = time.time()
        self._run_count += 1

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False


class MemoryScheduler:
    """Scheduler for background memory maintenance and periodic tasks."""

    def __init__(self):
        self._tasks: dict[str, ScheduledTask] = {}
        self._running: bool = False

    def add_task(
        self,
        name: str,
        interval: float,
        callback: Callable[[], None],
        run_immediately: bool = False,
    ) -> ScheduledTask:
        task = ScheduledTask(name, interval, callback, run_immediately)
        self._tasks[name] = task
        return task

    def remove_task(self, name: str) -> bool:
        return self._tasks.pop(name, None) is not None

    def get_task(self, name: str) -> ScheduledTask | None:
        return self._tasks.get(name)

    @property
    def tasks(self) -> dict[str, ScheduledTask]:
        return dict(self._tasks)

    @property
    def running(self) -> bool:
        return self._running

    async def start(self) -> None:
        self._running = True
        while self._running:
            due = [t for t in self._tasks.values() if t.is_due]
            for task in due:
                await task.execute()
            await asyncio.sleep(1.0)

    def stop(self) -> None:
        self._running = False

    def run_due(self) -> list[str]:
        ran: list[str] = []
        for task in self._tasks.values():
            if task.is_due:
                task.execute()
                ran.append(task.name)
        return ran

    def summary(self) -> dict[str, Any]:
        return {
            "task_count": len(self._tasks),
            "running": self._running,
            "tasks": {
                name: {
                    "interval": t.interval,
                    "enabled": t.enabled,
                    "run_count": t.run_count,
                    "last_run": t.last_run,
                }
                for name, t in self._tasks.items()
            },
        }
