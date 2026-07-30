from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class PipelineStatus(Enum):
    IDLE = "idle"
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Pipeline:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    status: PipelineStatus = PipelineStatus.IDLE
    stages: list[dict[str, Any]] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
