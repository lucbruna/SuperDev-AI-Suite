"""
Sync Scheduler - Schedule sync jobs
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Schedule:
    schedule_id: str
    job_id: str
    interval_seconds: int = 3600
    enabled: bool = True
    last_run: datetime | None = None
    next_run: datetime | None = None
    run_count: int = 0


class SyncScheduler:
    def __init__(self):
        self.schedules: dict[str, Schedule] = {}
        self.execution_log: list[dict[str, Any]] = []

    def create_schedule(self, job_id: str, interval_seconds: int = 3600) -> Schedule:
        schedule_id = f"sch_{len(self.schedules)}"
        schedule = Schedule(schedule_id=schedule_id, job_id=job_id, interval_seconds=interval_seconds)
        self.schedules[schedule_id] = schedule
        return schedule

    def enable(self, schedule_id: str) -> bool:
        schedule = self.schedules.get(schedule_id)
        if schedule:
            schedule.enabled = True
            return True
        return False

    def disable(self, schedule_id: str) -> bool:
        schedule = self.schedules.get(schedule_id)
        if schedule:
            schedule.enabled = False
            return True
        return False

    def get_due(self) -> list[Schedule]:
        now = datetime.now()
        return [s for s in self.schedules.values() if s.enabled and s.next_run and s.next_run <= now]

    def mark_executed(self, schedule_id: str) -> bool:
        schedule = self.schedules.get(schedule_id)
        if schedule:
            schedule.last_run = datetime.now()
            schedule.run_count += 1
            from datetime import timedelta
            schedule.next_run = datetime.now() + timedelta(seconds=schedule.interval_seconds)
            return True
        return False

    def get_schedule(self, schedule_id: str) -> Schedule | None:
        return self.schedules.get(schedule_id)

    def list_all(self) -> list[Schedule]:
        return list(self.schedules.values())

    def count(self) -> int:
        return len(self.schedules)
