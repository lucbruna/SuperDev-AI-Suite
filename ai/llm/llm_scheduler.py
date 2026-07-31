from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from .llm_logger import LLMLogger


@dataclass
class ScheduledTask:
    """Represents a scheduled LLM task."""
    task_id: str
    provider: str
    prompt: str
    execute_at: float
    priority: int = 0
    params: dict[str, Any] = field(default_factory=dict)
    callback: Callable[[dict[str, Any]], Any] | None = None


class LLMScheduler:
    """Schedules and manages deferred LLM execution."""

    def __init__(self, logger: LLMLogger) -> None:
        self._logger = logger
        self._queue: list[ScheduledTask] = []
        self._running = False
        self._task_id_counter = 0

    def schedule(self, provider: str, prompt: str, delay: float = 0.0, **kwargs: Any) -> str:
        self._task_id_counter += 1
        task_id = f"task_{self._task_id_counter}"
        task = ScheduledTask(
            task_id=task_id,
            provider=provider,
            prompt=prompt,
            execute_at=time.time() + delay,
            priority=kwargs.pop("priority", 0),
            params=kwargs,
            callback=kwargs.pop("callback", None),
        )
        self._queue.append(task)
        self._queue.sort(key=lambda t: (t.execute_at, -t.priority))
        self._logger.info(provider, f"Scheduled task {task_id} in {delay}s")
        return task_id

    def cancel(self, task_id: str) -> bool:
        before = len(self._queue)
        self._queue = [t for t in self._queue if t.task_id != task_id]
        return len(self._queue) < before

    @property
    def pending_count(self) -> int:
        now = time.time()
        return sum(1 for t in self._queue if t.execute_at > now)

    @property
    def overdue_count(self) -> int:
        now = time.time()
        return sum(1 for t in self._queue if t.execute_at <= now)

    def get_status(self) -> dict[str, Any]:
        return {
            "running": self._running,
            "pending": self.pending_count,
            "overdue": self.overdue_count,
            "queue_size": len(self._queue),
        }
