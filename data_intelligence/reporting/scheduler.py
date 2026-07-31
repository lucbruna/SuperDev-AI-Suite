"""Report scheduling (cron-like)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from data_intelligence.reporting.base import ReportingError

CRON_PARTS = ("minute", "hour", "day", "month", "weekday")


class ReportScheduler:
    """Decides whether a scheduled report should run now."""

    def __init__(self) -> None:
        self.jobs: dict[str, dict[str, Any]] = {}

    def schedule(self, report_id: str, cron: str) -> None:
        """Parses a 5-field cron expression and stores the job."""
        parts = cron.split()
        if len(parts) != 5:
            raise ReportingError(f"invalid cron expression: {cron!r}")
        for part, name in zip(parts, CRON_PARTS):
            self._validate(part, name)
        self.jobs[report_id] = {"cron": cron, "parts": dict(zip(CRON_PARTS,
                                                                parts)),
                                "last_run": None}

    def due(self, report_id: str,
            now: datetime | None = None) -> bool:
        """Returns True when the job's expression matches the moment."""
        job = self.jobs.get(report_id)
        if job is None:
            raise ReportingError(f"unknown scheduled report: {report_id}")
        now = now or datetime.now()
        parts = job["parts"]
        return (self._matches(parts["minute"], now.minute)
                and self._matches(parts["hour"], now.hour)
                and self._matches(parts["day"], now.day)
                and self._matches(parts["month"], now.month)
                and self._matches(parts["weekday"],
                                  (now.weekday() + 1) % 7))

    def mark_run(self, report_id: str, when: str | None = None) -> None:
        job = self.jobs.get(report_id)
        if job is None:
            raise ReportingError(f"unknown scheduled report: {report_id}")
        job["last_run"] = when or datetime.now().isoformat()

    def list_jobs(self) -> dict[str, Any]:
        return {rid: {"cron": j["cron"], "last_run": j["last_run"]}
                for rid, j in self.jobs.items()}

    @staticmethod
    def _matches(expr: str, value: int) -> bool:
        if expr == "*":
            return True
        for part in expr.split(","):
            if "-" in part:
                low, high = part.split("-")
                if int(low) <= value <= int(high):
                    return True
            elif "*/" in part:
                step = int(part.split("*/")[1])
                if step and value % step == 0:
                    return True
            elif part.isdigit() and int(part) == value:
                return True
        return False

    @staticmethod
    def _validate(part: str, name: str) -> None:
        import re
        if not re.match(r"^[0-9*,/\-]+$", part):
            raise ReportingError(f"invalid {name} expression: {part!r}")
