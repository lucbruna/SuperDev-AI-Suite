from __future__ import annotations

import logging
from typing import Any, Callable

from .worker_pool import WorkerPool
from .worker_manager import WorkerManager
from .worker_metrics import WorkerMetrics
from .worker_health import WorkerHealth


class WorkerEngine:
    """Central engine for managing worker lifecycle."""

    def __init__(self, max_workers: int = 4) -> None:
        self._pool = WorkerPool(max_workers)
        self._manager = WorkerManager()
        self._metrics = WorkerMetrics()
        self._health = WorkerHealth()
        self._log = logging.getLogger("superdev.workflow.workers")

    def start(self) -> None:
        self._pool.start()
        self._log.info("Worker engine started")

    def stop(self) -> None:
        self._pool.stop()
        self._log.info("Worker engine stopped")

    def submit(self, task_id: str, action: Callable[..., Any]) -> None:
        self._pool.submit(task_id, action)
        self._metrics.record_submission()
