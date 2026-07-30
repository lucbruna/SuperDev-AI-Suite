from __future__ import annotations

import time
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any


class AIMetrics:
    """Metrics collection for the AI engine."""

    def __init__(self):
        self._counters: dict[str, int] = defaultdict(int)
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._gauges: dict[str, float] = {}
        self._start_time: float = time.time()

    def increment(self, metric: str, value: int = 1) -> None:
        """Increment a counter metric."""
        self._counters[metric] += value

    def record(self, metric: str, value: float) -> None:
        """Record a histogram value."""
        self._histograms[metric].append(value)
        # Keep only last 1000 values
        if len(self._histograms[metric]) > 1000:
            self._histograms[metric] = self._histograms[metric][-1000:]

    def set_gauge(self, metric: str, value: float) -> None:
        """Set a gauge metric."""
        self._gauges[metric] = value

    def get_counter(self, metric: str) -> int:
        """Get the value of a counter."""
        return self._counters.get(metric, 0)

    def get_histogram_stats(self, metric: str) -> dict[str, float] | None:
        """Get statistics for a histogram metric."""
        values = self._histograms.get(metric)
        if not values:
            return None
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        return {
            "count": n,
            "min": sorted_vals[0],
            "max": sorted_vals[-1],
            "avg": sum(sorted_vals) / n,
            "p50": sorted_vals[n // 2],
            "p90": sorted_vals[int(n * 0.9)],
            "p99": sorted_vals[int(n * 0.99)],
        }

    def get_all_counters(self) -> dict[str, int]:
        """Get all counter metrics."""
        return dict(self._counters)

    def get_all_gauges(self) -> dict[str, float]:
        """Get all gauge metrics."""
        return dict(self._gauges)

    def reset(self) -> None:
        """Reset all metrics."""
        self._counters.clear()
        self._histograms.clear()
        self._gauges.clear()
        self._start_time = time.time()

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines: list[str] = []
        lines.append("# HELP ai_engine_metrics AI Engine metrics")
        lines.append("# TYPE ai_engine_metrics counter")
        for name, value in self._counters.items():
            safe_name = name.replace("-", "_").replace(" ", "_")
            lines.append(f'ai_{safe_name}_total {value}')

        for name, values in self._histograms.items():
            safe_name = name.replace("-", "_").replace(" ", "_")
            if values:
                lines.append(f'# TYPE ai_{safe_name}_duration_seconds histogram')
                for v in values[-10:]:  # Last 10 values
                    lines.append(f'ai_{safe_name}_duration_seconds {v}')

        for name, value in self._gauges.items():
            safe_name = name.replace("-", "_").replace(" ", "_")
            lines.append(f'ai_{safe_name} {value}')

        lines.append(f'ai_uptime_seconds {time.time() - self._start_time}')
        return "\n".join(lines) + "\n"

    def snapshot(self) -> dict[str, Any]:
        """Get a snapshot of all metrics."""
        histogram_stats = {}
        for metric in self._histograms:
            stats = self.get_histogram_stats(metric)
            if stats:
                histogram_stats[metric] = stats

        return {
            "counters": dict(self._counters),
            "histograms": histogram_stats,
            "gauges": dict(self._gauges),
            "uptime_seconds": time.time() - self._start_time,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def health(self) -> dict[str, Any]:
        """Get metrics subsystem health."""
        return {
            "status": "healthy",
            "counters": len(self._counters),
            "histograms": len(self._histograms),
            "gauges": len(self._gauges),
            "uptime_seconds": time.time() - self._start_time,
            "timestamp": datetime.now(UTC).isoformat(),
        }
