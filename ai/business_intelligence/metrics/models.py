"""Metrics models."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class AggregationType(Enum):
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE = "percentile"


class MetricStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class MetricDefinition:
    name: str
    metric_type: str
    description: str = ""
    unit: str = ""
    dimensions: List[str] = field(default_factory=list)
    aggregation: AggregationType = AggregationType.SUM
    retention_days: int = 30


@dataclass
class MetricValue:
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    dimensions: Dict[str, str] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class MetricThreshold:
    metric_name: str
    warning_min: Optional[float] = None
    warning_max: Optional[float] = None
    critical_min: Optional[float] = None
    critical_max: Optional[float] = None


@dataclass
class MetricAlert:
    alert_id: str
    metric_name: str
    status: MetricStatus
    current_value: float
    threshold: Optional[MetricThreshold] = None
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MetricSummary:
    name: str
    count: int = 0
    sum: float = 0.0
    avg: float = 0.0
    min_val: float = 0.0
    max_val: float = 0.0
    latest: float = 0.0
    status: MetricStatus = MetricStatus.UNKNOWN
