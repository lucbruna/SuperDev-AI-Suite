"""Data models for scheduling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SchedulerJob:
    """A scheduled job bound to a workflow."""

    job_id: str
    workflow_id: str
    cron: str | None = None
    interval_seconds: float | None = None
    enabled: bool = True
    last_run: float | None = None
    next_run_ts: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "workflow_id": self.workflow_id,
            "cron": self.cron,
            "interval_seconds": self.interval_seconds,
            "enabled": self.enabled,
            "last_run": self.last_run,
            "next_run_ts": self.next_run_ts,
        }
