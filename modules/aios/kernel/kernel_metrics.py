"""Kernel metrics — counters, gauges and timings for kernel activity."""
from __future__ import annotations
from time import monotonic
from typing import Any


class KernelMetrics:
    """In-memory metrics store (counters, gauges, timings)."""

    def __init__(self) -> None:
        self._counters: dict[str, int] = {}
        self._gauges: dict[str, float] = {}
        self._timings: dict[str, list[float]] = {}

    def increment(self, name: str, amount: int = 1) -> int:
        value = self._counters.get(name, 0) + amount
        self._counters[name] = value
        return value

    def set_gauge(self, name: str, value: float) -> None:
        self._gauges[name] = float(value)

    def record_timing(self, name: str, seconds: float) -> None:
        self._timings.setdefault(name, []).append(float(seconds))

    def timed(self, name: str) -> _Timing:
        return _Timing(self, name)

    def counter(self, name: str) -> int:
        return self._counters.get(name, 0)

    def timing_stats(self, name: str) -> dict[str, float]:
        samples = self._timings.get(name, [])
        if not samples:
            return {"count": 0, "avg_ms": 0.0, "min_ms": 0.0, "max_ms": 0.0}
        return {
            "count": len(samples),
            "avg_ms": round(sum(samples) / len(samples) * 1000, 3),
            "min_ms": round(min(samples) * 1000, 3),
            "max_ms": round(max(samples) * 1000, 3),
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "timings": {
                name: self.timing_stats(name) for name in sorted(self._timings)
            },
        }


class _Timing:
    def __init__(self, metrics: KernelMetrics, name: str) -> None:
        self._metrics = metrics
        self._name = name
        self._started = monotonic()

    def __enter__(self) -> _Timing:
        return self

    def __exit__(self, *exc: object) -> None:
        self._metrics.record_timing(self._name, monotonic() - self._started)


_kernel_metrics: KernelMetrics | None = None


def get_kernel_metrics() -> KernelMetrics:
    global _kernel_metrics
    if _kernel_metrics is None:
        _kernel_metrics = KernelMetrics()
    return _kernel_metrics
