from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TelemetryEvent:
    """Represents a single telemetry data point."""

    name: str
    data: dict[str, Any] = field(default_factory=dict)
    context: dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    severity: str = "info"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "data": self.data,
            "context": self.context,
            "timestamp": self.timestamp,
            "severity": self.severity,
        }
