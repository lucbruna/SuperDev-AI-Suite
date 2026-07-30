from __future__ import annotations

import logging
import threading
from typing import Any

from .worker_task import WorkerTask


class WorkerThread:
    """Single worker thread that processes tasks."""

    def __init__(self) -> None:
        self._thread: threading.Thread | None = None
        self._task: WorkerTask | None = None
        self._running = False
        self._lock = threading.Lock()
        self._log = logging.getLogger("superdev.workflow.workers.thread")

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def assign(self, task: WorkerTask) -> None:
        with self._lock:
            self._task = task

    def is_busy(self) -> bool:
        with self._lock:
            return self._task is not None

    def _run(self) -> None:
        while self._running:
            task: WorkerTask | None = None
            with self._lock:
                if self._task is not None:
                    task = self._task
                    self._task = None
            if task:
                try:
                    task.execute()
                except Exception as exc:
                    self._log.exception("Task %s failed: %s", task.id, exc)
