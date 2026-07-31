"""Factory Metrics - Performance metrics for factory operations."""
import statistics
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MetricPoint:
    name: str
    value: float
    unit: str = ""
    project_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class MetricSummary:
    name: str
    count: int = 0
    min_val: float = 0.0
    max_val: float = 0.0
    avg_val: float = 0.0
    latest: float = 0.0


class FactoryMetrics:
    def __init__(self):
        self.metrics: dict[str, list[MetricPoint]] = {}
        self.counters: dict[str, int] = {}
        self.gauges: dict[str, float] = {}

    def record(self, name: str, value: float, unit: str = "", project_id: str = "", tags: dict[str, str] = None) -> MetricPoint:
        point = MetricPoint(name=name, value=value, unit=unit, project_id=project_id, tags=tags or {})
        self.metrics.setdefault(name, []).append(point)
        return point

    def increment(self, counter: str, amount: int = 1) -> int:
        self.counters[counter] = self.counters.get(counter, 0) + amount
        return self.counters[counter]

    def set_gauge(self, gauge: str, value: float) -> None:
        self.gauges[gauge] = value

    def get_gauge(self, gauge: str) -> float:
        return self.gauges.get(gauge, 0.0)

    def get_counter(self, counter: str) -> int:
        return self.counters.get(counter, 0)

    def get_summary(self, name: str) -> MetricSummary:
        points = self.metrics.get(name, [])
        if not points:
            return MetricSummary(name=name)
        values = [p.value for p in points]
        return MetricSummary(name=name, count=len(values), min_val=min(values), max_val=max(values), avg_val=statistics.mean(values), latest=values[-1])

    def get_points(self, name: str, limit: int = 100) -> list[MetricPoint]:
        return self.metrics.get(name, [])[-limit:]

    def list_metrics(self) -> list[str]:
        return list(self.metrics.keys())

    def count(self) -> int:
        return sum(len(v) for v in self.metrics.values())
