"""Deterministic metrics: counters, gauges and histograms."""
from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["MetricSnapshot", "MetricsRegistry"]


@dataclass(slots=True)
class MetricSnapshot:
    """A point-in-time copy of every metric."""

    counters: dict[str, int] = field(default_factory=dict)
    gauges: dict[str, float] = field(default_factory=dict)
    histograms: dict[str, dict[str, float]] = field(default_factory=dict)


class MetricsRegistry:
    """Counters, gauges and histograms with deterministic reporting."""

    def __init__(self) -> None:
        self._counters: dict[str, int] = {}
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = {}

    def increment(self, name: str, by: int = 1) -> None:
        self._counters[name] = self._counters.get(name, 0) + by

    def gauge(self, name: str, value: float) -> None:
        self._gauges[name] = float(value)

    def histogram(self, name: str, value: float) -> None:
        self._histograms.setdefault(name, []).append(float(value))

    def snapshot(self) -> MetricSnapshot:
        histograms = {
            name: {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "sum": sum(values),
                "mean": sum(values) / len(values),
            }
            for name, values in self._histograms.items()
        }
        return MetricSnapshot(
            counters=dict(self._counters),
            gauges=dict(self._gauges),
            histograms=histograms,
        )

    def clear(self) -> None:
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()

    def report(self) -> str:
        """Deterministic, sorted multi-line text of the current snapshot."""
        snap = self.snapshot()
        lines: list[str] = []
        for name in sorted(snap.counters):
            lines.append(f"counter {name} = {snap.counters[name]}")
        for name in sorted(snap.gauges):
            lines.append(f"gauge {name} = {snap.gauges[name]:g}")
        for name in sorted(snap.histograms):
            hist = snap.histograms[name]
            lines.append(
                f"histogram {name} = count={hist['count']:g} "
                f"mean={hist['mean']:g} min={hist['min']:g} max={hist['max']:g}"
            )
        return "\n".join(lines)
