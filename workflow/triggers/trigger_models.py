from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TriggerStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FIRING = "firing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Trigger:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    trigger_type: str = "manual"
    config: dict[str, Any] = field(default_factory=dict)
    status: TriggerStatus = TriggerStatus.INACTIVE
    context: dict[str, Any] = field(default_factory=dict)
