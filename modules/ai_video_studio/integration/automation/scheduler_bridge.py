"""Scheduler Bridge — next-run computation for cron expressions."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any


class SchedulerBridge:
    """Computes the next run for a 5-field cron expression (best-effort)."""

    def next_run(self, cron: str = "0 6 * * *") -> dict[str, Any]:
        parts = cron.split()
        if len(parts) != 5:
            return {"ok": False, "error": "cron must have 5 fields", "cron": cron}
        minute, hour = parts[0], parts[1]
        try:
            base = datetime.now().replace(second=0, microsecond=0)
            nxt = base + timedelta(minutes=1)
            if minute.isdigit():
                nxt = nxt.replace(minute=int(minute) % 60)
                if nxt < base:
                    nxt += timedelta(hours=1)
            if hour.isdigit():
                nxt = nxt.replace(hour=int(hour) % 24)
                if nxt < base:
                    nxt += timedelta(days=1)
            return {"cron": cron, "next_run": nxt.isoformat()}
        except ValueError as e:
            return {"ok": False, "error": str(e), "cron": cron}


_scheduler_bridge: SchedulerBridge | None = None


def get_scheduler_bridge() -> SchedulerBridge:
    global _scheduler_bridge
    if _scheduler_bridge is None:
        _scheduler_bridge = SchedulerBridge()
    return _scheduler_bridge
