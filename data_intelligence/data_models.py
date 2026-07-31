"""Data models for the Data Intelligence & Analytics Engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SourceType(Enum):
    SQL = "sql"
    MONGODB = "mongodb"
    API = "api"
    FILE = "file"          # CSV / JSON / Excel
    STREAM = "stream"
    CLOUD = "cloud"
    ERP = "erp"
    CRM = "crm"
    IOT = "iot"
    LOG = "log"


class PipelineStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class AnalyticsLevel(Enum):
    DESCRIPTIVE = "descriptive"
    DIAGNOSTIC = "diagnostic"
    PREDICTIVE = "predictive"
    PRESCRIPTIVE = "prescriptive"


class ModelStatus(Enum):
    TRAINED = "trained"
    EVALUATED = "evaluated"
    DEPLOYED = "deployed"
    FAILED = "failed"


class ReportFormat(Enum):
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    CSV = "csv"


class DataClassification(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


@dataclass
class DataSource:
    """A configured source of data."""

    source_id: str
    name: str
    source_type: SourceType
    config: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class DataRecord:
    """A single raw or processed data item."""

    record_id: str
    source_id: str
    data: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    ingested_at: float = 0.0


@dataclass
class PipelineSpec:
    """Definition of a data pipeline."""

    pipeline_id: str
    name: str
    stages: list[dict[str, Any]] = field(default_factory=list)
    schedule_cron: str | None = None
    enabled: bool = True


@dataclass
class AnalyticsResult:
    """Outcome of an analytics computation."""

    level: AnalyticsLevel
    metric: str
    value: Any = None
    detail: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"level": self.level.value, "metric": self.metric,
                "value": self.value, "detail": self.detail}


@dataclass
class PredictionResult:
    """Outcome of a machine learning prediction."""

    prediction_id: str
    model_id: str
    value: Any = None
    confidence: float = 0.0
    features: dict[str, Any] = field(default_factory=dict)
    detail: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"prediction_id": self.prediction_id,
                "model_id": self.model_id, "value": self.value,
                "confidence": self.confidence}


@dataclass
class DashboardSpec:
    """Definition of a dashboard."""

    dashboard_id: str
    name: str
    audience: str = "executive"  # executive | operations | it
    widgets: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ModelRecord:
    """A trained machine learning model."""

    model_id: str
    name: str
    algorithm: str
    status: ModelStatus = ModelStatus.TRAINED
    metrics: dict[str, Any] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReportSpec:
    """Definition of an automatic report."""

    report_id: str
    name: str
    report_type: str = "executive"  # executive | financial | operational
    format: ReportFormat = ReportFormat.JSON
    schedule_cron: str | None = None


@dataclass
class GovernanceRecord:
    """A governance decision about a dataset."""

    record_id: str
    dataset: str
    policy: str
    action: str
    detail: dict[str, Any] = field(default_factory=dict)
