"""BI Metrics — Performance metrics for BI operations."""
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


class BIMetrics:
    def __init__(self):
        self.metrics: dict[str, list[MetricPoint]] = {}

    def record(self, name: str, value: float, unit: str = "", project_id: str = "", tags: dict[str, str] = None) -> MetricPoint:
        point = MetricPoint(name=name, value=value, unit=unit, project_id=project_id, tags=tags or {})
        self.metrics.setdefault(name, []).append(point)
        return point

    def get_summary(self, name: str) -> MetricSummary:
        points = self.metrics.get(name, [])
        if not points:
            return MetricSummary(name=name)
        values = [p.value for p in points]
        return MetricSummary(
            name=name,
            count=len(values),
            min_val=min(values),
            max_val=max(values),
            avg_val=statistics.mean(values),
            latest=values[-1],
        )

    def get_all_metrics(self) -> list[MetricSummary]:
        return [self.get_summary(name) for name in self.metrics]

    def count(self) -> int:
        return sum(len(v) for v in self.metrics.values())
