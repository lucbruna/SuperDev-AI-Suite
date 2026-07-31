"""Analytics data models."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class AnalysisType(Enum):
    DESCRIPTIVE = "descriptive"
    DIAGNOSTIC = "diagnostic"
    PREDICTIVE = "predictive"
    PRESCRIPTIVE = "prescriptive"


class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class InsightType(Enum):
    TREND = "trend"
    ANOMALY = "anomaly"
    CORRELATION = "correlation"
    PATTERN = "pattern"


@dataclass
class DataPoint:
    timestamp: datetime
    value: float
    metric_name: str
    dimensions: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Insight:
    insight_id: str
    insight_type: InsightType
    title: str
    description: str
    confidence: float
    data_points: list[DataPoint] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AnalysisRequest:
    request_id: str
    analysis_type: AnalysisType
    query: str
    time_range_start: datetime | None = None
    time_range_end: datetime | None = None
    dimensions: list[str] = field(default_factory=list)
    filters: dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    request_id: str
    status: str = "pending"
    data_points: list[DataPoint] = field(default_factory=list)
    insights: list[Insight] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    error: str | None = None
