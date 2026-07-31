"""Ingestion models."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class ConnectorType(Enum):
    DATABASE = "database"
    API = "api"
    FILE = "file"
    STREAM = "stream"
    WEBHOOK = "webhook"


class IngestionStatus(Enum):
    IDLE = "idle"
    CONNECTING = "connecting"
    INGESTING = "ingesting"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Connector:
    connector_id: str
    name: str = ""
    connector_type: ConnectorType = ConnectorType.DATABASE
    config: Dict[str, Any] = field(default_factory=dict)
    status: IngestionStatus = IngestionStatus.IDLE
    records_ingested: int = 0
    last_run: Optional[datetime] = None


@dataclass
class IngestionBatch:
    batch_id: str
    connector_id: str = ""
    records: List[Dict[str, Any]] = field(default_factory=list)
    status: IngestionStatus = IngestionStatus.IDLE
    record_count: int = 0
    error_count: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class DataSource:
    source_id: str
    name: str = ""
    connector_type: ConnectorType = ConnectorType.DATABASE
    connection_string: str = ""
    is_active: bool = True
    last_sync: Optional[datetime] = None


@dataclass
class IngestionLog:
    log_id: str = ""
    connector_id: str = ""
    batch_id: str = ""
    action: str = ""
    status: str = ""
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
