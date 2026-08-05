"""AIOS Kernel Metrics — deterministic counters, gauges and histograms.

Pure in-memory metrics. A sink may be attached to forward samples to
an external metrics system at compose time.
"""

from __future__ import annotations

from typing import Any, Callable

SampleSink = Callable[[str, Any], None]


class KernelMetrics:
    """Tiny metrics registry (counters / gauges / histograms)."""

    def __init__(self, sink: SampleSink | None = None) -> None:
        self._sink = sink
        self._counters: dict[str, int] = {}
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = {}

    def _emit(self, name: str, value: Any) -> None:
        if self._sink is not None:
            self._sink(name, value)

    # -- counters ------------------------------------------------------
    def inc(self, name: str, delta: int = 1) -> int:
        value = self._counters.get(name, 0) + delta
        self._counters[name] = value
        self._emit(name, value)
        return value

    def counter(self, name: str) -> int:
        return self._counters.get(name, 0)

    # -- gauges --------------------------------------------------------
    def set_gauge(self, name: str, value: float) -> None:
        self._gauges[name] = float(value)
        self._emit(name, value)

    def gauge(self, name: str) -> float | None:
        return self._gauges.get(name)

    # -- histograms ----------------------------------------------------
    def record(self, name: str, value: float) -> None:
        self._histograms.setdefault(name, []).append(float(value))
        self._emit(name, value)

    def histogram(self, name: str) -> dict[str, Any]:
        samples = self._histograms.get(name, [])
        if not samples:
            return {"count": 0, "min": None, "max": None, "mean": None, "p95": None}
        ordered = sorted(samples)
        p95 = ordered[max(0, int(len(ordered) * 0.95) - 1)]
        return {
            "count": len(ordered),
            "min": ordered[0],
            "max": ordered[-1],
            "mean": round(sum(ordered) / len(ordered), 4),
            "p95": p95,
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {name: self.histogram(name) for name in sorted(self._histograms)},
        }
