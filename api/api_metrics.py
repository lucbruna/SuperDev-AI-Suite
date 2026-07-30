from __future__ import annotations

import time
from collections import defaultdict
from typing import Any


class APIMetrics:
    """Collects and exposes API-level metrics."""

    def __init__(self) -> None:
        self._counters: dict[str, int] = defaultdict(int)
        self._timings: dict[str, list[float]] = defaultdict(list)
        self._gauges: dict[str, float] = {}
        self._start_time = time.time()

    def increment(self, metric: str, tags: dict[str, str] | None = None) -> None:
        key = metric
        if tags:
            tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
            key = f"{metric}[{tag_str}]"
        self._counters[key] += 1

    def timing(self, metric: str, duration_ms: float, tags: dict[str, str] | None = None) -> None:
        key = metric
        if tags:
            tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
            key = f"{metric}[{tag_str}]"
        self._timings[key].append(duration_ms)

    def gauge(self, metric: str, value: float) -> None:
        self._gauges[metric] = value

    def get_counter(self, metric: str) -> int:
        return self._counters.get(metric, 0)

    def get_counters(self) -> dict[str, int]:
        return dict(self._counters)

    def get_timing_summary(self, metric: str) -> dict[str, float]:
        vals = self._timings.get(metric, [])
        if not vals:
            return {"avg": 0.0, "p50": 0.0, "p95": 0.0, "p99": 0.0, "count": 0}
        sorted_vals = sorted(vals)
        n = len(sorted_vals)
        return {
            "avg": sum(vals) / n,
            "p50": sorted_vals[int(n * 0.5)],
            "p95": sorted_vals[int(n * 0.95)],
            "p99": sorted_vals[max(0, int(n * 0.99) - 1)],
            "count": n,
        }

    @property
    def uptime_seconds(self) -> float:
        return time.time() - self._start_time

    @property
    def total_requests(self) -> int:
        return self._counters.get("requests", 0)

    def to_dict(self) -> dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "uptime_seconds": self.uptime_seconds,
            "total_requests": self.total_requests,
        }

    def reset(self) -> None:
        self._counters.clear()
        self._timings.clear()
        self._gauges.clear()
        self._start_time = time.time()
