from __future__ import annotations

import logging
from typing import Any, Callable

from .worker_pool import WorkerPool
from .worker_health import WorkerHealth
from .worker_metrics import WorkerMetrics


class WorkerManager:
    """Manages worker pool lifecycle and health."""

    def __init__(self, max_workers: int = 4) -> None:
        self._pool = WorkerPool(max_workers)
        self._health = WorkerHealth()
        self._metrics = WorkerMetrics()
        self._log = logging.getLogger("superdev.workflow.workers.manager")

    def start(self) -> None:
        self._pool.start()
        self._log.info("Worker manager started")

    def stop(self) -> None:
        self._pool.stop()

    def submit(self, task_id: str, action: Callable[..., Any]) -> None:
        self._pool.submit(task_id, action)
        self._metrics.record_submission()

    def health_summary(self) -> dict[str, Any]:
        return self._health.summary()

    def metrics_snapshot(self) -> dict[str, Any]:
        return self._metrics.snapshot()
