"""
Integration Metrics - Performance monitoring
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import statistics


@dataclass
class MetricPoint:
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class IntegrationMetric:
    metric_id: str
    integration_id: str
    metric_name: str
    value: float
    unit: str = ""
    recorded_at: datetime = field(default_factory=datetime.now)


class IntegrationMetrics:
    def __init__(self):
        self.metrics: Dict[str, List[MetricPoint]] = {}
        self.integration_metrics: Dict[str, List[IntegrationMetric]] = {}
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = {}

    def record(self, name: str, value: float, tags: Dict[str, str] = None) -> MetricPoint:
        point = MetricPoint(name=name, value=value, tags=tags or {})
        self.metrics.setdefault(name, []).append(point)
        return point

    def increment(self, name: str, amount: int = 1) -> int:
        self.counters[name] = self.counters.get(name, 0) + amount
        return self.counters[name]

    def set_gauge(self, name: str, value: float) -> None:
        self.gauges[name] = value

    def get_gauge(self, name: str) -> Optional[float]:
        return self.gauges.get(name)

    def observe(self, name: str, value: float) -> None:
        self.histograms.setdefault(name, []).append(value)

    def get_histogram_stats(self, name: str) -> Dict[str, float]:
        values = self.histograms.get(name, [])
        if not values:
            return {"count": 0, "mean": 0, "min": 0, "max": 0, "p50": 0, "p95": 0, "p99": 0}
        sorted_vals = sorted(values)
        return {"count": len(values), "mean": statistics.mean(values), "min": min(values), "max": max(values), "p50": sorted_vals[len(sorted_vals) // 2], "p95": sorted_vals[int(len(sorted_vals) * 0.95)], "p99": sorted_vals[int(len(sorted_vals) * 0.99)]}

    def record_integration_metric(self, integration_id: str, metric_name: str, value: float, unit: str = "") -> IntegrationMetric:
        metric = IntegrationMetric(metric_id=hashlib.sha256(f"{integration_id}{metric_name}{datetime.now().isoformat()}".encode()).hexdigest()[:16], integration_id=integration_id, metric_name=metric_name, value=value, unit=unit)
        self.integration_metrics.setdefault(integration_id, []).append(metric)
        return metric

    def get_integration_metrics(self, integration_id: str) -> List[IntegrationMetric]:
        return self.integration_metrics.get(integration_id, [])

    def get_metric_points(self, name: str, limit: int = 100) -> List[MetricPoint]:
        return self.metrics.get(name, [])[-limit:]

    def get_counter(self, name: str) -> int:
        return self.counters.get(name, 0)

    def reset_counter(self, name: str) -> None:
        self.counters[name] = 0

    def count(self) -> int:
        return sum(len(v) for v in self.metrics.values())
