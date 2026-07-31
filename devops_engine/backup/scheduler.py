"""Backup scheduling (Volume 37, Fase 5)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from devops_engine.devops_protocols import new_id, now


@dataclass
class ScheduledBackup:
    """A recurring backup schedule."""
    schedule_id: str
    target: str
    interval_hours: float = 24.0
    last_run: float = 0.0
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class BackupScheduler:
    """Schedules recurring backups and detects due runs."""

    def __init__(self) -> None:
        self._schedules: dict[str, ScheduledBackup] = {}

    def schedule(self, target: str,
                 interval_hours: float = 24.0) -> ScheduledBackup:
        schedule = ScheduledBackup(
            schedule_id=new_id("schedule"),
            target=target,
            interval_hours=float(interval_hours),
            created_at=now(),
        )
        self._schedules[schedule.schedule_id] = schedule
        return schedule

    def due(self, schedule_id: str, now_ts: float) -> bool:
        schedule = self._schedules.get(schedule_id)
        if schedule is None:
            return False
        elapsed = max(0.0, now_ts - schedule.last_run)
        return elapsed >= schedule.interval_hours * 3600.0

    def mark_run(self, schedule_id: str, now_ts: float) -> bool:
        schedule = self._schedules.get(schedule_id)
        if schedule is None:
            return False
        schedule.last_run = now_ts
        return True

    def get(self, schedule_id: str) -> ScheduledBackup | None:
        return self._schedules.get(schedule_id)

    def list(self) -> list[ScheduledBackup]:
        return list(self._schedules.values())

    def count(self) -> int:
        return len(self._schedules)
