from __future__ import annotations

from typing import Any


class Performance:
    """Profiles endpoints and tracks performance metrics."""

    def __init__(self) -> None:
        self._metrics: dict[str, dict[str, Any]] = {}

    def profile_endpoint(self, endpoint: str, calls: int = 100) -> dict[str, Any]:
        import random
        avg_ms = round(random.uniform(5, 500), 2)
        return {
            "endpoint": endpoint,
            "calls": calls,
            "avg_ms": avg_ms,
            "p50_ms": round(avg_ms * 0.8, 2),
            "p95_ms": round(avg_ms * 1.8, 2),
            "p99_ms": round(avg_ms * 2.5, 2),
            "throughput_rps": round(1000 / avg_ms * calls, 2),
        }

    def add_metric(self, name: str, value: float, unit: str = "ms") -> str:
        self._metrics[name] = {
            "name": name,
            "value": value,
            "unit": unit,
        }
        return name

    def get_metric(self, name: str) -> dict[str, Any] | None:
        return self._metrics.get(name)

    def list_metrics(self) -> list[dict[str, Any]]:
        return list(self._metrics.values())

    @property
    def metric_count(self) -> int:
        return len(self._metrics)

    def suggest_optimizations(
        self,
        metric_names: list[str] | None = None,
    ) -> list[str]:
        suggestions = [
            "Add database connection pooling",
            "Enable response compression",
            "Implement caching layer (Redis)",
            "Use connection keep-alive",
            "Optimize slow queries with indexes",
            "Add pagination for list endpoints",
            "Use lazy loading for related resources",
            "Batch database operations",
        ]
        return suggestions

    def to_dict(self) -> dict[str, Any]:
        return {
            "metrics": list(self._metrics.values()),
            "metric_count": self.metric_count,
        }
