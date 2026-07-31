"""In-process metrics collector for request tracking and monitoring."""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MetricPoint:
    """A single metric data point."""

    name: str
    value: float
    timestamp: float = field(default_factory=time.time)
    labels: dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """Thread-safe in-process metrics collector.

    Tracks request counts, durations, error rates, and custom counters.
    Replace with prometheus_client in production for Prometheus integration.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._request_count: dict[str, int] = defaultdict(int)
        self._request_duration: dict[str, list[float]] = defaultdict(list)
        self._error_count: dict[str, int] = defaultdict(int)
        self._custom_counters: dict[str, int] = defaultdict(int)
        self._start_time = time.time()

    def record_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_seconds: float,
    ) -> None:
        """Record an HTTP request metric."""
        key = f"{method} {path}"
        with self._lock:
            self._request_count[key] += 1
            self._request_duration[key].append(duration_seconds)
            # Keep only last 1000 durations per endpoint
            if len(self._request_duration[key]) > 1000:
                self._request_duration[key] = self._request_duration[key][-1000:]
            if status_code >= 400:
                self._error_count[f"{key} {status_code}"] += 1

    def record_error(self, endpoint: str, error_type: str) -> None:
        """Record an application error."""
        with self._lock:
            self._error_count[f"{endpoint} {error_type}"] += 1

    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment a custom counter."""
        with self._lock:
            self._custom_counters[name] += value

    def get_metrics(self) -> dict[str, Any]:
        """Get all collected metrics as a dictionary."""
        with self._lock:
            uptime = time.time() - self._start_time

            # Calculate request stats
            total_requests = sum(self._request_count.values())
            total_errors = sum(
                v for k, v in self._error_count.items()
                if not k.split()[-1].isdigit() or int(k.split()[-1]) >= 500
            )

            # Calculate average durations
            avg_durations = {}
            for key, durations in self._request_duration.items():
                if durations:
                    avg_durations[key] = {
                        "avg_ms": round(sum(durations) / len(durations) * 1000, 2),
                        "min_ms": round(min(durations) * 1000, 2),
                        "max_ms": round(max(durations) * 1000, 2),
                        "count": len(durations),
                    }

            return {
                "uptime_seconds": round(uptime, 2),
                "total_requests": total_requests,
                "total_errors": total_errors,
                "error_rate_pct": round(
                    (total_errors / total_requests * 100) if total_requests > 0 else 0, 2
                ),
                "requests_by_endpoint": dict(self._request_count),
                "errors": dict(self._error_count),
                "durations": avg_durations,
                "custom_counters": dict(self._custom_counters),
            }

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._request_count.clear()
            self._request_duration.clear()
            self._error_count.clear()
            self._custom_counters.clear()
            self._start_time = time.time()


# Singleton instance
_collector: MetricsCollector | None = None
_collector_lock = threading.Lock()


def get_metrics_collector() -> MetricsCollector:
    """Get or create the global metrics collector singleton."""
    global _collector
    if _collector is None:
        with _collector_lock:
            if _collector is None:
                _collector = MetricsCollector()
    return _collector
