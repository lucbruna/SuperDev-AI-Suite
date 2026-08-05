"""Image scheduler — queue image generation tasks."""
from __future__ import annotations

import time
from collections import deque
from typing import Any


class ImageScheduler:
    """Simple queue with concurrency limit for image jobs."""

    def __init__(self, max_concurrent: int = 4) -> None:
        self.max_concurrent = max_concurrent
        self._queue: deque[dict[str, Any]] = deque()
        self._running: dict[str, dict[str, Any]] = {}
        self._done: list[str] = []

    def enqueue(self, job: dict[str, Any]) -> str:
        job.setdefault("queued_at", time.time())
        self._queue.append(job)
        return job["id"]

    def next(self) -> dict[str, Any] | None:
        if len(self._running) >= self.max_concurrent:
            return None
        if not self._queue:
            return None
        job = self._queue.popleft()
        self._running[job["id"]] = job
        return job

    def complete(self, job_id: str) -> None:
        self._running.pop(job_id, None)
        self._done.append(job_id)

    def pending(self) -> int:
        return len(self._queue)

    def running(self) -> int:
        return len(self._running)


_image_scheduler: ImageScheduler | None = None


def get_image_scheduler() -> ImageScheduler:
    global _image_scheduler
    if _image_scheduler is None:
        _image_scheduler = ImageScheduler()
    return _image_scheduler
