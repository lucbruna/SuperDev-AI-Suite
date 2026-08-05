"""Incident: record of a detected failure and its remediation outcome."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

INCIDENT_STATUSES = ("open", "resolved")


@dataclass
class Incident:
    incident_id: str
    source: str
    critical: bool
    message: str
    status: str = "open"
    created_seq: int = 0
    resolved_seq: Optional[int] = None
    actions_applied: list[str] = field(default_factory=list)
    attempts: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "source": self.source,
            "critical": self.critical,
            "message": self.message,
            "status": self.status,
            "created_seq": self.created_seq,
            "resolved_seq": self.resolved_seq,
            "actions_applied": list(self.actions_applied),
            "attempts": self.attempts,
        }
