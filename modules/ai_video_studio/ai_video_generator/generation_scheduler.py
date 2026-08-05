"""Generation scheduler — queue, priority and retry handling for jobs."""
from __future__ import annotations

import time
from collections import deque
from typing import Any


class GenerationScheduler:
    """Simple FIFO scheduler with priority tiers and retry support."""

    PRIORITY_HIGH = 0
    PRIORITY_NORMAL = 1
    PRIORITY_LOW = 2

    def __init__(self, max_concurrent: int = 2) -> None:
        self.max_concurrent = max_concurrent
        self._queues: dict[int, deque[dict[str, Any]]] = {
            self.PRIORITY_HIGH: deque(),
            self.PRIORITY_NORMAL: deque(),
            self.PRIORITY_LOW: deque(),
        }
        self._running: dict[str, dict[str, Any]] = {}
        self._retries: dict[str, int] = {}

    def enqueue(self, job: dict[str, Any], *, priority: int = PRIORITY_NORMAL) -> str:
        job.setdefault("queued_at", time.time())
        self._queues[priority].append(job)
        return job["id"]

    def next(self) -> dict[str, Any] | None:
        """Return the next schedulable job or None when saturated."""
        if len(self._running) >= self.max_concurrent:
            return None
        for priority in (self.PRIORITY_HIGH, self.PRIORITY_NORMAL, self.PRIORITY_LOW):
            if self._queues[priority]:
                job = self._queues[priority].popleft()
                self._running[job["id"]] = job
                return job
        return None

    def complete(self, job_id: str) -> None:
        self._running.pop(job_id, None)

    def fail(self, job_id: str, *, max_retries: int = 2) -> bool:
        """Requeue the running job for retry; returns True when retried."""
        job = self._running.pop(job_id, None)
        if job is None:
            return False
        count = self._retries.get(job_id, 0)
        if count >= max_retries:
            return False
        self._retries[job_id] = count + 1
        job["retry"] = count + 1
        self.enqueue(job, priority=self.PRIORITY_NORMAL)
        return True

    def pending_count(self) -> int:
        return sum(len(q) for q in self._queues.values())

    def running_count(self) -> int:
        return len(self._running)

    def snapshot(self) -> dict[str, Any]:
        return {
            "pending": self.pending_count(),
            "running": self.running_count(),
            "max_concurrent": self.max_concurrent,
            "retries": dict(self._retries),
        }


_generation_scheduler: GenerationScheduler | None = None


def get_generation_scheduler() -> GenerationScheduler:
    global _generation_scheduler
    if _generation_scheduler is None:
        _generation_scheduler = GenerationScheduler()
    return _generation_scheduler
