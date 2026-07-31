"""Data models for automation monitoring."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MonitorStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class MonitorCheck:
    """Result of a single health check."""

    check_id: str
    name: str
    status: MonitorStatus
    detail: str = ""
    checked_at: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "name": self.name,
            "status": self.status.value,
            "detail": self.detail,
            "checked_at": self.checked_at,
        }


@dataclass
class MonitorAlert:
    """An alert raised when a check is not healthy."""

    alert_id: str
    check_id: str
    level: str  # warning | critical
    message: str
    timestamp: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "check_id": self.check_id,
            "level": self.level,
            "message": self.message,
            "timestamp": self.timestamp,
        }
