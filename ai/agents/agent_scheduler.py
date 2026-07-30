from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class ScheduledTask:
    """A task scheduled for future execution."""

    def __init__(self, task_id: str, task: Dict[str, Any], run_at: float) -> None:
        self._task_id = task_id
        self._task = task
        self._run_at = run_at
        self._executed: bool = False

    @property
    def task_id(self) -> str:
        return self._task_id

    @property
    def task(self) -> Dict[str, Any]:
        return self._task

    @property
    def run_at(self) -> float:
        return self._run_at

    @property
    def executed(self) -> bool:
        return self._executed

    def mark_executed(self) -> None:
        self._executed = True


class AgentScheduler:
    """Handles task scheduling for agents."""

    def __init__(self) -> None:
        self._tasks: Dict[str, ScheduledTask] = {}
        self._scheduled_count: int = 0

    @property
    def task_count(self) -> int:
        return len(self._tasks)

    @property
    def scheduled_count(self) -> int:
        return self._scheduled_count

    def schedule(self, task_id: str, task: Dict[str, Any], delay: float = 0.0) -> None:
        run_at = time.time() + delay
        self._tasks[task_id] = ScheduledTask(task_id, task, run_at)
        self._scheduled_count += 1

    def cancel(self, task_id: str) -> bool:
        return self._tasks.pop(task_id, None) is not None

    def pending(self) -> List[ScheduledTask]:
        now = time.time()
        return [t for t in self._tasks.values() if not t.executed and t.run_at <= now]

    def clear(self) -> None:
        self._tasks.clear()
