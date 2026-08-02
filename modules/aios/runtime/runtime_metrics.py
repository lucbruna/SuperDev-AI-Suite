"""Runtime metrics — kernel-backed counters and timings for runtime activity."""
from __future__ import annotations
from typing import Any

from modules.aios.kernel.kernel_metrics import get_kernel_metrics


class RuntimeMetrics:
    """Wraps the kernel metrics store with runtime-specific helpers."""

    def __init__(self) -> None:
        self._metrics = get_kernel_metrics()

    def session_started(self) -> None:
        self._metrics.increment("runtime.sessions.started")

    def session_finished(self, *, ok: bool) -> None:
        bucket = "succeeded" if ok else "failed"
        self._metrics.increment(f"runtime.sessions.{bucket}")

    def record_duration(self, seconds: float) -> None:
        self._metrics.record_timing("runtime.session.duration", seconds)

    def active_sessions(self, count: int) -> None:
        self._metrics.set_gauge("runtime.sessions.active", count)

    def snapshot(self) -> dict[str, Any]:
        return {
            "sessions": {
                "started": self._metrics.counter("runtime.sessions.started"),
                "succeeded": self._metrics.counter("runtime.sessions.succeeded"),
                "failed": self._metrics.counter("runtime.sessions.failed"),
            },
            "active": self._metrics.counter("runtime.sessions.active"),
            "duration": self._metrics.timing_stats("runtime.session.duration"),
        }


_runtime_metrics: RuntimeMetrics | None = None


def get_runtime_metrics() -> RuntimeMetrics:
    global _runtime_metrics
    if _runtime_metrics is None:
        _runtime_metrics = RuntimeMetrics()
    return _runtime_metrics


__all__ = ["RuntimeMetrics", "get_runtime_metrics"]
