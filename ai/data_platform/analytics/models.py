"""Analytics models."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class QueryType(Enum):
    SELECT = "select"
    AGGREGATE = "aggregate"
    JOIN = "join"
    GROUP_BY = "group_by"
    TIME_SERIES = "time_series"


class InsightType(Enum):
    TREND = "trend"
    ANOMALY = "anomaly"
    CORRELATION = "correlation"
    FORECAST = "forecast"
    SUMMARY = "summary"


@dataclass
class AnalyticsQuery:
    query_id: str
    dataset: str = ""
    query_type: QueryType = QueryType.SELECT
    filters: Dict[str, Any] = field(default_factory=dict)
    group_by: List[str] = field(default_factory=list)
    metrics: List[str] = field(default_factory=list)
    limit: int = 1000
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class QueryResult:
    result_id: str
    query_id: str = ""
    rows: List[Dict[str, Any]] = field(default_factory=list)
    row_count: int = 0
    execution_ms: float = 0.0


@dataclass
class Insight:
    insight_id: str
    dataset: str = ""
    insight_type: InsightType = InsightType.SUMMARY
    title: str = ""
    description: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Dashboard:
    dashboard_id: str
    name: str = ""
    widgets: List[Dict[str, Any]] = field(default_factory=list)
    owner: str = ""
    is_public: bool = False
    created_at: datetime = field(default_factory=datetime.now)
