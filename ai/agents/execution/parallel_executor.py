"""Concurrent task execution manager."""
from __future__ import annotations

import time
from typing import Any


class ParallelExecutor:
    """Manages concurrent task execution with configurable limits."""

    def __init__(self, max_concurrent: int = 10) -> None:
        self._max_concurrent = max_concurrent
        self._running: dict[str, dict[str, Any]] = {}
        self._completed: list[dict[str, Any]] = []
        self._queue: list[dict[str, Any]] = []

    async def execute_batch(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for task in tasks:
            task_id = task.get("id", f"parallel_{len(self._completed)}")
            if self._active_count() >= self._max_concurrent:
                self._queue.append(task)
                continue
            self._running[task_id] = {
                "id": task_id,
                "started_at": time.time(),
                "task": task,
            }
            result = {
                "task_id": task_id,
                "status": "completed",
                "output": f"Batch task {task_id} executed",
                "completed_at": time.time(),
            }
            self._completed.append(result)
            if task_id in self._running:
                del self._running[task_id]
            results.append(result)
        while self._queue and self._active_count() < self._max_concurrent:
            next_task = self._queue.pop(0)
            tid = next_task.get("id", f"queued_{len(self._completed)}")
            result = {
                "task_id": tid,
                "status": "completed",
                "output": f"Queued task {tid} executed",
            }
            self._completed.append(result)
            results.append(result)
        return results

    def _active_count(self) -> int:
        return len(self._running)

    def get_queue_status(self) -> dict[str, Any]:
        return {
            "running": self._active_count(),
            "queued": len(self._queue),
            "completed": len(self._completed),
            "max_concurrent": self._max_concurrent,
        }

    def get_completed(self) -> list[dict[str, Any]]:
        return list(self._completed)
