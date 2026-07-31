"""
Sync Scheduler - Schedule sync jobs
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Schedule:
    schedule_id: str
    job_id: str
    interval_seconds: int = 3600
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0


class SyncScheduler:
    def __init__(self):
        self.schedules: Dict[str, Schedule] = {}
        self.execution_log: List[Dict[str, Any]] = []

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

    def get_due(self) -> List[Schedule]:
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

    def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        return self.schedules.get(schedule_id)

    def list_all(self) -> List[Schedule]:
        return list(self.schedules.values())

    def count(self) -> int:
        return len(self.schedules)
