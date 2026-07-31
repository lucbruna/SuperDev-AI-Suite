"""Processing models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class TransformType(Enum):
    MAP = "map"
    FILTER = "filter"
    AGGREGATE = "aggregate"
    JOIN = "join"
    NORMALIZE = "normalize"
    DEDUPLICATE = "deduplicate"


class ProcessingStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TransformRule:
    rule_id: str
    name: str = ""
    transform_type: TransformType = TransformType.MAP
    config: dict[str, Any] = field(default_factory=dict)
    order: int = 0
    enabled: bool = True


@dataclass
class ProcessingJob:
    job_id: str
    name: str = ""
    dataset: str = ""
    rules: list[TransformRule] = field(default_factory=list)
    status: ProcessingStatus = ProcessingStatus.IDLE
    input_count: int = 0
    output_count: int = 0
    error_count: int = 0
    started_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass
class ProcessingResult:
    result_id: str
    job_id: str = ""
    status: ProcessingStatus = ProcessingStatus.IDLE
    records_in: int = 0
    records_out: int = 0
    duration_ms: float = 0.0
    errors: list[str] = field(default_factory=list)
