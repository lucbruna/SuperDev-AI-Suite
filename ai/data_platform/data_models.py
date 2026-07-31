"""Data Platform Models — Core data models for the autonomous data platform."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DataSourceType(Enum):
    DATABASE = "database"
    API = "api"
    FILE = "file"
    STREAM = "stream"
    SENSOR = "sensor"
    IoT = "iot"


class DataFormat(Enum):
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    AVRO = "avro"
    ORC = "orc"
    XML = "xml"


class PipelineStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class DataQualityLevel(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


class StorageTier(Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    ARCHIVE = "archive"


@dataclass
class DataSource:
    source_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    source_type: DataSourceType = DataSourceType.DATABASE
    connection_string: str = ""
    format: DataFormat = DataFormat.JSON
    status: str = "active"
    last_sync: datetime | None = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DataRecord:
    record_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_id: str = ""
    dataset: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    quality_score: float = 1.0
    tags: list[str] = field(default_factory=list)


@dataclass
class DataPipeline:
    pipeline_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    source_id: str = ""
    steps: list[dict[str, Any]] = field(default_factory=list)
    status: PipelineStatus = PipelineStatus.IDLE
    records_processed: int = 0
    error_count: int = 0
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DataSchema:
    schema_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    version: str = "1.0"
    fields: list[dict[str, Any]] = field(default_factory=list)
    dataset: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DataCatalogEntry:
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    dataset: str = ""
    description: str = ""
    owner: str = ""
    schema_id: str = ""
    record_count: int = 0
    size_bytes: int = 0
    quality_level: DataQualityLevel = DataQualityLevel.GOOD
    tags: list[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class DataPartition:
    partition_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    dataset: str = ""
    key: str = ""
    tier: StorageTier = StorageTier.HOT
    record_count: int = 0
    size_bytes: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None


@dataclass
class DataLineage:
    lineage_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    dataset: str = ""
    source_datasets: list[str] = field(default_factory=list)
    transformation: str = ""
    created_at: datetime = field(default_factory=datetime.now)
