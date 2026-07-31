"""ETL models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ETLStatus(Enum):
    IDLE = "idle"
    EXTRACTING = "extracting"
    TRANSFORMING = "transforming"
    LOADING = "loading"
    COMPLETED = "completed"
    FAILED = "failed"


class StepType(Enum):
    EXTRACT = "extract"
    TRANSFORM = "transform"
    LOAD = "load"
    VALIDATE = "validate"


@dataclass
class ETLStep:
    step_id: str
    name: str = ""
    step_type: StepType = StepType.EXTRACT
    config: dict[str, Any] = field(default_factory=dict)
    order: int = 0
    status: ETLStatus = ETLStatus.IDLE


@dataclass
class ETLPipeline:
    pipeline_id: str
    name: str = ""
    steps: list[ETLStep] = field(default_factory=list)
    status: ETLStatus = ETLStatus.IDLE
    records_extracted: int = 0
    records_transformed: int = 0
    records_loaded: int = 0
    error_count: int = 0
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ETLLog:
    log_id: str
    pipeline_id: str = ""
    step_id: str = ""
    action: str = ""
    status: str = ""
    records_processed: int = 0
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
