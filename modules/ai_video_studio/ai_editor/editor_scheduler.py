"""Editor scheduler — prioritised task queue with a background worker.

Tasks (edits, proxy builds, renders) are submitted with a priority and
processed in order by a daemon worker thread. Supports cancel-by-id and a
``run_once`` mode for synchronous/embedded use without threads.
"""
from __future__ import annotations

import heapq
import threading
import time
import uuid
from typing import Any, Callable

from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.scheduler")


class EditorScheduler:
    def __init__(self, *, workers: int = 1, run_background: bool = True) -> None:
        self._queue: list[tuple[int, float, str, Callable[..., Any], tuple, dict]] = []
        self._results: dict[str, Any] = {}
        self._running: set[str] = set()
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._threads: list[threading.Thread] = []
        if run_background:
            for _ in range(max(1, workers)):
                t = threading.Thread(target=self._loop, daemon=True)
                t.start()
                self._threads.append(t)

    def submit(self, fn: Callable[..., Any], *args: Any, priority: int = 5, **kwargs: Any) -> str:
        """Schedule ``fn``; lower priority runs first. Returns a task id."""
        task_id = uuid.uuid4().hex[:10]
        with self._lock:
            heapq.heappush(self._queue, (int(priority), time.monotonic(), task_id, fn, args, kwargs))
        return task_id

    def status(self, task_id: str) -> str:
        with self._lock:
            if task_id in self._results:
                return "done"
            if task_id in self._running:
                return "running"
            if any(item[2] == task_id for item in self._queue):
                return "queued"
        return "unknown"

    def result(self, task_id: str) -> Any:
        with self._lock:
            return self._results.get(task_id)

    def cancel(self, task_id: str) -> bool:
        with self._lock:
            before = len(self._queue)
            self._queue = [item for item in self._queue if item[2] != task_id]
            heapq.heapify(self._queue)
        return len(self._queue) != before

    def run_once(self, timeout: float | None = 5.0) -> bool:
        """Execute the next queued task inline (blocking). Returns True if any ran."""
        with self._lock:
            if not self._queue:
                return False
            _, _, task_id, fn, args, kwargs = heapq.heappop(self._queue)
            self._running.add(task_id)
        try:
            self._results[task_id] = fn(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001 — surface as result
            self._results[task_id] = {"error": str(exc)}
        finally:
            self._running.discard(task_id)
        return True

    def _loop(self) -> None:
        while not self._stop.is_set():
            if not self.run_once(timeout=0.1):
                self._stop.wait(0.1)

    def shutdown(self) -> None:
        self._stop.set()
        for t in self._threads:
            t.join(timeout=1.0)
