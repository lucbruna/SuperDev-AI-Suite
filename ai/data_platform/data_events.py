"""Data Platform Events — Event definitions for data platform operations."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DataEventType(Enum):
    SOURCE_REGISTERED = "source_registered"
    DATA_INGESTED = "data_ingested"
    PIPELINE_STARTED = "pipeline_started"
    PIPELINE_COMPLETED = "pipeline_completed"
    PIPELINE_FAILED = "pipeline_failed"
    QUALITY_CHECK = "quality_check"
    SCHEMA_REGISTERED = "schema_registered"
    CATALOG_UPDATED = "catalog_updated"
    ALERT_TRIGGERED = "alert_triggered"


@dataclass
class DataEvent:
    event_id: str = ""
    event_type: DataEventType = DataEventType.DATA_INGESTED
    source_id: str = ""
    dataset: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    severity: str = "info"
