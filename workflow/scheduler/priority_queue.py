from __future__ import annotations

import heapq
import time
from typing import Any, Callable


class SchedulerPriorityQueue:
    """Priority queue for scheduled jobs."""

    def __init__(self) -> None:
        self._queue: list[tuple[float, int, str, Callable[..., Any]]] = []
        self._counter = 0

    def push(self, run_at: float, job_id: str, action: Callable[..., Any]) -> None:
        self._counter += 1
        heapq.heappush(self._queue, (run_at, self._counter, job_id, action))

    def pop(self) -> tuple[float, str, Callable[..., Any]] | None:
        if not self._queue:
            return None
        run_at, _, job_id, action = heapq.heappop(self._queue)
        return run_at, job_id, action

    def peek(self) -> float | None:
        return self._queue[0][0] if self._queue else None

    def due_jobs(self, now: float | None = None) -> list[tuple[str, Callable[..., Any]]]:
        now = now or time.time()
        due: list[tuple[str, Callable[..., Any]]] = []
        while self._queue and self._queue[0][0] <= now:
            _, _, job_id, action = heapq.heappop(self._queue)
            due.append((job_id, action))
        return due

    def __len__(self) -> int:
        return len(self._queue)
