"""X Scheduler — best post times for X (Volume 7)."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

_WINDOWS = [(7, 9), (12, 13), (19, 21)]
_BEST_DAYS = (0, 1, 2, 3, 4)  # Mon-Fri


class XScheduler:
    """Compute recommended X posting slots."""

    def next_slot(self, *, days: int = 7) -> dict:
        """Find the next recommended posting time within *days*."""
        now = datetime.now()
        for delta in range(days * 24):
            candidate = now + timedelta(hours=delta)
            if candidate.weekday() not in _BEST_DAYS:
                continue
            hour = candidate.hour
            for start, end in _WINDOWS:
                if start <= hour < end:
                    return {
                        "iso": candidate.isoformat(),
                        "window": f"{start:02d}:00-{end:02d}:00",
                    }
        raise RuntimeError("No slot found")  # pragma: no cover

    def weekly_plan(self) -> list[dict]:
        """Return one recommended slot per weekday."""
        plan = []
        now = datetime.now()
        for day_offset in range(7):
            for hour in range(24):
                dt = now + timedelta(days=day_offset, hours=hour)
                if dt.weekday() not in _BEST_DAYS:
                    continue
                if any(start <= hour < end for start, end in _WINDOWS):
                    plan.append({
                        "weekday_offset": day_offset,
                        "weekday": dt.strftime("%A"),
                        "iso": dt.isoformat(),
                        "window": f"{hour:02d}:00-{min(hour + 2, 24):02d}:00",
                    })
                    break
        return plan

    def stats(self) -> dict[str, int]:
        return {"windows": len(_WINDOWS), "best_days": len(_BEST_DAYS)}


_SCHEDULER: XScheduler | None = None


def get_x_scheduler() -> XScheduler:
    """Get the module-level singleton X scheduler."""
    global _SCHEDULER
    if _SCHEDULER is None:
        _SCHEDULER = XScheduler()
    return _SCHEDULER
