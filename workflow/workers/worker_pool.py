from __future__ import annotations

import logging
from typing import Any, Callable

from .worker_thread import WorkerThread
from .worker_task import WorkerTask


class WorkerPool:
    """Manages a pool of worker threads."""

    def __init__(self, max_workers: int = 4) -> None:
        self._max = max_workers
        self._threads: list[WorkerThread] = []
        self._log = logging.getLogger("superdev.workflow.workers.pool")

    def start(self) -> None:
        for _ in range(self._max):
            t = WorkerThread()
            t.start()
            self._threads.append(t)

    def stop(self) -> None:
        for t in self._threads:
            t.stop()

    def submit(self, task_id: str, action: Callable[..., Any]) -> None:
        task = WorkerTask(task_id, action)
        for t in self._threads:
            if not t.is_busy():
                t.assign(task)
                return
        self._log.warning("No available worker for %s", task_id)
