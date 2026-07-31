from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DataSourceType(str, Enum):
    API = "api"
    DATABASE = "database"
    FILE = "file"
    EVENT = "event"
    LOG = "log"
    AGENT = "agent"
    PROJECT = "project"
    STREAM = "stream"


class DataFormat(str, Enum):
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    AVRO = "avro"
    XML = "xml"
    SQL = "sql"
    TEXT = "text"
    BINARY = "binary"


class DataState(str, Enum):
    RAW = "raw"
    CLEANED = "cleaned"
    PROCESSED = "processed"
    CURATED = "curated"


class DataQualityStatus(str, Enum):
    UNKNOWN = "unknown"
    GOOD = "good"
    WARNING = "warning"
    BAD = "bad"


class PipelineStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class PipelineRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class EtlJobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ModelStatus(str, Enum):
    DRAFT = "draft"
    TRAINING = "training"
    READY = "ready"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"
    FAILED = "failed"


class DataClassification(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class RetentionPolicy(str, Enum):
    KEEP = "keep"
    DELETE_AFTER_DAYS = "delete_after_days"
    ARCHIVE_AFTER_DAYS = "archive_after_days"


class ChartType(str, Enum):
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"
    HEATMAP = "heatmap"
    MAP = "map"
    TABLE = "table"
    FUNNEL = "funnel"
    GAUGE = "gauge"


class ReportFormat(str, Enum):
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"


class StreamWindow(str, Enum):
    TUMBLING = "tumbling"
    SLIDING = "sliding"
    SESSION = "session"


class AnomalySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class LogEntry:
    message: str = ""
    level: LogLevel = LogLevel.INFO
    logger: str = ""
    timestamp: float = field(default_factory=time.time)
    labels: dict[str, str] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class DataRecord:
    """A single record of data collected from any source."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    source: str = ""
    timestamp: float = field(default_factory=time.time)
    data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    state: DataState = DataState.RAW
    quality: DataQualityStatus = DataQualityStatus.UNKNOWN


@dataclass
class DataBatch:
    """A collection of records sharing the same source."""

    batch_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    source: str = ""
    records: list[DataRecord] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    size_bytes: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class IngestionSource:
    source_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    source_type: DataSourceType = DataSourceType.API
    config: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    last_ingested_at: float | None = None


@dataclass
class IngestionResult:
    source: str = ""
    records_count: int = 0
    errors: list[str] = field(default_factory=list)
    duration_ms: float = 0.0
    status: str = "succeeded"
    started_at: float = field(default_factory=time.time)


@dataclass
class DataQualityReport:
    asset_id: str = ""
    completeness: float = 0.0
    accuracy: float = 0.0
    consistency: float = 0.0
    uniqueness: float = 0.0
    validity: float = 0.0
    issues: list[dict[str, Any]] = field(default_factory=list)
    generated_at: float = field(default_factory=time.time)


@dataclass
class PipelineDefinition:
    pipeline_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    description: str = ""
    steps: list[dict[str, Any]] = field(default_factory=list)
    schedule: str = ""  # cron-like expression
    status: PipelineStatus = PipelineStatus.DRAFT
    enabled: bool = True
    created_at: float = field(default_factory=time.time)


@dataclass
class PipelineRun:
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    pipeline_id: str = ""
    status: PipelineRunStatus = PipelineRunStatus.PENDING
    started_at: float = field(default_factory=time.time)
    completed_at: float | None = None
    steps_progress: dict[str, str] = field(default_factory=dict)
    error: str = ""


@dataclass
class Dimension:
    name: str = ""
    columns: list[str] = field(default_factory=list)
    description: str = ""


@dataclass
class FactTable:
    name: str = ""
    measures: list[str] = field(default_factory=list)
    dimensions: list[str] = field(default_factory=list)


@dataclass
class StarSchema:
    name: str = ""
    fact: FactTable | None = None
    dimensions: list[Dimension] = field(default_factory=list)


@dataclass
class LakeObject:
    object_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    path: str = ""
    zone: str = "raw"  # raw | processed | curated
    format: DataFormat = DataFormat.JSON
    size_bytes: int = 0
    checksum: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    uploaded_at: float = field(default_factory=time.time)


@dataclass
class EtlJob:
    job_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    extract: dict[str, Any] = field(default_factory=dict)
    transform: dict[str, Any] = field(default_factory=dict)
    load: dict[str, Any] = field(default_factory=dict)
    schedule: str = ""
    status: EtlJobStatus = EtlJobStatus.PENDING
    last_run_at: float | None = None


@dataclass
class KPI:
    kpi_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    metric: str = ""
    target: float = 0.0
    current: float = 0.0
    unit: str = ""
    period: str = "monthly"


@dataclass
class MetricDefinition:
    metric_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    expression: str = ""
    unit: str = ""
    description: str = ""


@dataclass
class DashboardConfig:
    dashboard_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    widgets: list[dict[str, Any]] = field(default_factory=list)
    owner: str = ""
    permissions: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class MLModel:
    model_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    algorithm: str = ""
    status: ModelStatus = ModelStatus.DRAFT
    version: str = "0.1.0"
    metrics: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


@dataclass
class ModelVersion:
    version_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    model_id: str = ""
    version: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)
    artifact_path: str = ""
    created_at: float = field(default_factory=time.time)


@dataclass
class TrainingRun:
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    model_id: str = ""
    dataset: str = ""
    hyperparameters: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    started_at: float = field(default_factory=time.time)
    completed_at: float | None = None


@dataclass
class ForecastResult:
    forecast_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    series_name: str = ""
    horizon: int = 0
    values: list[float] = field(default_factory=list)
    confidence: float = 0.0
    method: str = "moving_average"
    created_at: float = field(default_factory=time.time)


@dataclass
class Report:
    report_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    title: str = ""
    kind: str = "executive"  # executive | technical | financial | operational
    format: ReportFormat = ReportFormat.MARKDOWN
    sections: list[dict[str, Any]] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)
    generated_at: float = field(default_factory=time.time)


@dataclass
class GovernancePolicy:
    policy_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    rules: list[dict[str, Any]] = field(default_factory=list)
    scope: str = ""
    enabled: bool = True


@dataclass
class DataAsset:
    asset_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    asset_type: str = ""
    owner: str = ""
    classification: DataClassification = DataClassification.INTERNAL
    retention: RetentionPolicy = RetentionPolicy.KEEP
    lineage: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamEvent:
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    stream: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    partition: int = 0


@dataclass
class AnomalyAlert:
    alert_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    metric: str = ""
    severity: AnomalySeverity = AnomalySeverity.MEDIUM
    message: str = ""
    timestamp: float = field(default_factory=time.time)
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsResult:
    analysis_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    kind: str = ""  # descriptive | diagnostic | predictive | prescriptive
    results: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


__all__ = [
    "DataSourceType", "DataFormat", "DataState", "DataQualityStatus",
    "PipelineStatus", "PipelineRunStatus", "EtlJobStatus", "ModelStatus",
    "DataClassification", "RetentionPolicy", "ChartType", "ReportFormat",
    "StreamWindow", "AnomalySeverity", "LogLevel",
    "DataRecord", "DataBatch", "IngestionSource", "IngestionResult",
    "LogEntry",
    "DataQualityReport", "PipelineDefinition", "PipelineRun",
    "Dimension", "FactTable", "StarSchema", "LakeObject", "EtlJob",
    "KPI", "MetricDefinition", "DashboardConfig", "MLModel", "ModelVersion",
    "TrainingRun", "ForecastResult", "Report", "GovernancePolicy",
    "DataAsset", "StreamEvent", "AnomalyAlert", "AnalyticsResult",
]
