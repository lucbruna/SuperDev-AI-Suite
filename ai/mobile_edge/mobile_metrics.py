"""Mobile Metrics - Performance and usage metrics for mobile/edge."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import statistics


@dataclass
class MetricPoint:
    metric_name: str
    value: float
    unit: str = ""
    device_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class MetricSummary:
    metric_name: str
    count: int = 0
    min_val: float = 0.0
    max_val: float = 0.0
    avg_val: float = 0.0
    latest: float = 0.0


class MobileMetrics:
    def __init__(self):
        self.metrics: Dict[str, List[MetricPoint]] = {}
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}

    def record(self, metric_name: str, value: float, unit: str = "", device_id: str = "", tags: Dict[str, str] = None) -> MetricPoint:
        point = MetricPoint(metric_name=metric_name, value=value, unit=unit, device_id=device_id, tags=tags or {})
        self.metrics.setdefault(metric_name, []).append(point)
        return point

    def increment(self, counter_name: str, amount: int = 1) -> int:
        self.counters[counter_name] = self.counters.get(counter_name, 0) + amount
        return self.counters[counter_name]

    def set_gauge(self, gauge_name: str, value: float) -> None:
        self.gauges[gauge_name] = value

    def get_gauge(self, gauge_name: str) -> float:
        return self.gauges.get(gauge_name, 0.0)

    def get_counter(self, counter_name: str) -> int:
        return self.counters.get(counter_name, 0)

    def get_summary(self, metric_name: str) -> MetricSummary:
        points = self.metrics.get(metric_name, [])
        if not points:
            return MetricSummary(metric_name=metric_name)
        values = [p.value for p in points]
        return MetricSummary(
            metric_name=metric_name,
            count=len(values),
            min_val=min(values),
            max_val=max(values),
            avg_val=statistics.mean(values),
            latest=values[-1],
        )

    def get_points(self, metric_name: str, limit: int = 100, device_id: str = None) -> List[MetricPoint]:
        points = self.metrics.get(metric_name, [])
        if device_id:
            points = [p for p in points if p.device_id == device_id]
        return points[-limit:]

    def list_metrics(self) -> List[str]:
        return list(self.metrics.keys())

    def count(self) -> int:
        return sum(len(v) for v in self.metrics.values())
