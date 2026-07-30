from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RecoveryStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class RecoveryPlan:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    target_type: str = ""
    target_id: str = ""
    steps: list[dict[str, Any]] = field(default_factory=list)
    status: RecoveryStatus = RecoveryStatus.PENDING
    error: str | None = None
