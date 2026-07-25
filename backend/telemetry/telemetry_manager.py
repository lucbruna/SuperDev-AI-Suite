from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from backend.utils.uuid_utils import generate_uuid


@dataclass
class MetricPoint:
    name: str
    value: float
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class TelemetryManager:
    """Telemetry collection and export."""

    def __init__(self):
        self._metrics: list[MetricPoint] = []
        self._traces: list[dict[str, Any]] = []
        self._max_metrics = 10000

    def record_metric(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        point = MetricPoint(name=name, value=value, labels=labels or {})
        self._metrics.append(point)
        if len(self._metrics) > self._max_metrics:
            self._metrics = self._metrics[-self._max_metrics:]

    def record_trace(self, name: str, duration_ms: float, status: str = "ok", metadata: dict[str, Any] | None = None) -> None:
        trace = {
            "id": generate_uuid(),
            "name": name,
            "duration_ms": duration_ms,
            "status": status,
            "metadata": metadata or {},
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self._traces.append(trace)

    def get_metrics(self, name: str | None = None, limit: int = 100) -> list[MetricPoint]:
        metrics = self._metrics
        if name:
            metrics = [m for m in metrics if m.name == name]
        return metrics[-limit:]

    def get_traces(self, name: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        traces = self._traces
        if name:
            traces = [t for t in traces if t["name"] == name]
        return traces[-limit:]

    def get_metric_summary(self, name: str) -> dict[str, Any]:
        values = [m.value for m in self._metrics if m.name == name]
        if not values:
            return {"name": name, "count": 0}
        return {
            "name": name,
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "sum": sum(values),
        }

    def clear(self) -> None:
        self._metrics.clear()
        self._traces.clear()


telemetry_manager = TelemetryManager()
