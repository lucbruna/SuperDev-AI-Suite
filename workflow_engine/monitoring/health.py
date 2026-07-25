from __future__ import annotations

import time
from typing import Any

from workflow_engine.monitoring.metrics import WorkflowMetrics


class WorkflowHealth:
    _instance: WorkflowHealth | None = None

    def __new__(cls) -> WorkflowHealth:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._start_time = time.time()
            cls._instance._active_executions = 0
            cls._instance._queue_depth = 0
        return cls._instance

    def set_active_executions(self, count: int) -> None:
        self._active_executions = count

    def set_queue_depth(self, depth: int) -> None:
        self._queue_depth = depth

    def check(self) -> dict[str, Any]:
        metrics = WorkflowMetrics()
        snap = metrics.snapshot()
        uptime_seconds = time.time() - self._start_time
        total = snap["total_executions"]
        error_rate = snap["total_failures"] / total if total > 0 else 0.0

        return {
            "status": "healthy" if error_rate < 0.5 else "degraded",
            "active_executions": self._active_executions,
            "queue_depth": self._queue_depth,
            "error_rate": error_rate,
            "uptime_seconds": uptime_seconds,
            "uptime_formatted": self._format_uptime(uptime_seconds),
            "timestamp": time.time(),
        }

    @staticmethod
    def _format_uptime(seconds: float) -> str:
        days, remainder = divmod(int(seconds), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, secs = divmod(remainder, 60)
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        parts.append(f"{secs}s")
        return " ".join(parts)
