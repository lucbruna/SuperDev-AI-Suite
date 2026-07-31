"""CX Metrics — Performance metrics for CX operations."""
import statistics
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CXMetricPoint:
    name: str
    value: float
    unit: str = ""
    project_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class CXMetricSummary:
    name: str
    count: int = 0
    min_val: float = 0.0
    max_val: float = 0.0
    avg_val: float = 0.0
    latest: float = 0.0


class CXMetrics:
    def __init__(self):
        self.metrics: dict[str, list[CXMetricPoint]] = {}

    def record(self, name: str, value: float, unit: str = "", project_id: str = "", tags: dict[str, str] | None = None) -> CXMetricPoint:
        point = CXMetricPoint(name=name, value=value, unit=unit, project_id=project_id, tags=tags or {})
        self.metrics.setdefault(name, []).append(point)
        return point

    def get_summary(self, name: str) -> CXMetricSummary:
        points = self.metrics.get(name, [])
        if not points:
            return CXMetricSummary(name=name)
        values = [p.value for p in points]
        return CXMetricSummary(
            name=name,
            count=len(values),
            min_val=min(values),
            max_val=max(values),
            avg_val=statistics.mean(values),
            latest=values[-1],
        )

    def get_all_metrics(self) -> list[CXMetricSummary]:
        return [self.get_summary(name) for name in self.metrics]

    def count(self) -> int:
        return sum(len(v) for v in self.metrics.values())
