from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class IntegrationStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


@dataclass
class Integration:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    integration_type: str = ""
    config: dict[str, Any] = field(default_factory=dict)
    status: IntegrationStatus = IntegrationStatus.INACTIVE
