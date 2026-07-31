"""
Metrics Panel Component
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    PERCENTAGE = "percentage"
    CURRENCY = "currency"


@dataclass
class Metric:
    name: str
    value: float
    metric_type: MetricType = MetricType.COUNTER
    unit: str = ""
    min_value: float = 0
    max_value: float = 100
    target: Optional[float] = None
    history: List[float] = field(default_factory=list)


class MetricsPanel:
    def __init__(self):
        self.metrics: List[Metric] = []
        self.refresh_interval: int = 5000
        
    def add_metric(self, metric: Metric) -> None:
        self.metrics.append(metric)
        
    def update_metric(self, name: str, value: float) -> None:
        for m in self.metrics:
            if m.name == name:
                m.value = value
                m.history.append(value)
                if len(m.history) > 100:
                    m.history = m.history[-100:]
                return
                
    def get_metric(self, name: str) -> Optional[Metric]:
        return next((m for m in self.metrics if m.name == name), None)
        
    def render(self) -> Dict[str, Any]:
        return {
            "metrics": [{"name": m.name, "value": m.value, "type": m.metric_type.value, "unit": m.unit} for m in self.metrics],
            "refreshInterval": self.refresh_interval,
        }
