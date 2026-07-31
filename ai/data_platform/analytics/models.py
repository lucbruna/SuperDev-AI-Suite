"""Analytics models."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


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
    filters: dict[str, Any] = field(default_factory=dict)
    group_by: list[str] = field(default_factory=list)
    metrics: list[str] = field(default_factory=list)
    limit: int = 1000
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class QueryResult:
    result_id: str
    query_id: str = ""
    rows: list[dict[str, Any]] = field(default_factory=list)
    row_count: int = 0
    execution_ms: float = 0.0


@dataclass
class Insight:
    insight_id: str
    dataset: str = ""
    insight_type: InsightType = InsightType.SUMMARY
    title: str = ""
    description: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Dashboard:
    dashboard_id: str
    name: str = ""
    widgets: list[dict[str, Any]] = field(default_factory=list)
    owner: str = ""
    is_public: bool = False
    created_at: datetime = field(default_factory=datetime.now)
