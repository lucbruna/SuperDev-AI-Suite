from __future__ import annotations

import logging
from typing import Any


class WorkerPool:
    """Manages a pool of workers for parallel execution."""

    def __init__(self, size: int = 4) -> None:
        self._log = logging.getLogger("superdev.code.execution.workers")
        self._size = size
        self._workers: list[dict[str, Any]] = []

    def start(self) -> None:
        self._log.info("Starting worker pool (size=%d)", self._size)
        self._workers = [{"id": f"worker-{i}", "status": "idle"} for i in range(self._size)]

    def stop(self) -> None:
        self._log.info("Stopping worker pool")
        self._workers.clear()

    @property
    def available(self) -> int:
        return sum(1 for w in self._workers if w["status"] == "idle")

    @property
    def busy(self) -> int:
        return sum(1 for w in self._workers if w["status"] == "busy")
