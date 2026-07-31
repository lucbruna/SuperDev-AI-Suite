"""
Availability Monitor - Uptime tracking
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any


@dataclass
class AvailabilityRecord:
    integration_id: str
    is_available: bool
    checked_at: datetime = field(default_factory=datetime.now)
    response_time_ms: float = 0.0
    status_code: int = 200


class AvailabilityMonitor:
    def __init__(self):
        self.records: dict[str, list[AvailabilityRecord]] = {}
        self.sla_targets: dict[str, float] = {}

    def record(
        self, integration_id: str, is_available: bool, response_time_ms: float = 0.0, status_code: int = 200
    ) -> AvailabilityRecord:
        rec = AvailabilityRecord(
            integration_id=integration_id,
            is_available=is_available,
            response_time_ms=response_time_ms,
            status_code=status_code,
        )
        self.records.setdefault(integration_id, []).append(rec)
        return rec

    def set_sla(self, integration_id: str, target_percent: float) -> None:
        self.sla_targets[integration_id] = target_percent

    def get_uptime(self, integration_id: str, hours: int = 24) -> float:
        records = self.records.get(integration_id, [])
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [r for r in records if r.checked_at > cutoff]
        if not recent:
            return 100.0
        available = sum(1 for r in recent if r.is_available)
        return (available / len(recent)) * 100

    def check_sla(self, integration_id: str) -> dict[str, Any]:
        uptime = self.get_uptime(integration_id)
        target = self.sla_targets.get(integration_id, 99.9)
        return {"integration_id": integration_id, "uptime": uptime, "target": target, "met": uptime >= target}

    def get_records(self, integration_id: str, limit: int = 100) -> list[AvailabilityRecord]:
        return self.records.get(integration_id, [])[-limit:]

    def count(self) -> int:
        return sum(len(v) for v in self.records.values())
