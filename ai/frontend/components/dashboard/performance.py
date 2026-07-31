"""
Performance Dashboard
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class PerformanceMetric:
    name: str
    current: float
    average: float = 0
    peak: float = 0
    unit: str = "ms"
    threshold_warning: float = 0
    threshold_critical: float = 0


class PerformanceDashboard:
    def __init__(self):
        self.metrics: list[PerformanceMetric] = []
        self.time_range: str = "1h"

    def add_metric(self, metric: PerformanceMetric) -> None:
        self.metrics.append(metric)

    def update(self, name: str, value: float) -> None:
        for m in self.metrics:
            if m.name == name:
                m.current = value
                m.peak = max(m.peak, value)
                return

    def get_health(self) -> str:
        for m in self.metrics:
            if m.threshold_critical > 0 and m.current > m.threshold_critical:
                return "critical"
            if m.threshold_warning > 0 and m.current > m.threshold_warning:
                return "warning"
        return "healthy"

    def render(self) -> dict[str, Any]:
        return {
            "metrics": [{"name": m.name, "current": m.current, "unit": m.unit} for m in self.metrics],
            "health": self.get_health(),
            "timeRange": self.time_range,
        }
