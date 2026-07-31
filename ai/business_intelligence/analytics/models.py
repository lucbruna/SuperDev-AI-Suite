"""Analytics data models."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


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
    dimensions: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Insight:
    insight_id: str
    insight_type: InsightType
    title: str
    description: str
    confidence: float
    data_points: List[DataPoint] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AnalysisRequest:
    request_id: str
    analysis_type: AnalysisType
    query: str
    time_range_start: Optional[datetime] = None
    time_range_end: Optional[datetime] = None
    dimensions: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    request_id: str
    status: str = "pending"
    data_points: List[DataPoint] = field(default_factory=list)
    insights: List[Insight] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    error: Optional[str] = None
