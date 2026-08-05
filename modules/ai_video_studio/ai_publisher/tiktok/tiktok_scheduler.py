"""TikTok Scheduler — best post times for TikTok (Volume 7)."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

_WINDOWS = [(18, 22), (12, 14)]


class TikTokScheduler:
    """Compute recommended TikTok posting slots."""

    def next_slot(self, *, days: int = 7) -> dict:
        """Find the next recommended posting time within *days*."""
        now = datetime.now()
        for delta in range(days * 24):
            candidate = now + timedelta(hours=delta)
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
                if any(start <= hour < end for start, end in _WINDOWS):
                    plan.append({
                        "weekday_offset": day_offset,
                        "iso": dt.isoformat(),
                        "window": f"{hour:02d}:00-{min(hour + 2, 24):02d}:00",
                    })
                    break
        return plan

    def stats(self) -> dict[str, int]:
        return {"windows": len(_WINDOWS)}


_SCHEDULER: TikTokScheduler | None = None


def get_tiktok_scheduler() -> TikTokScheduler:
    """Get the module-level singleton TikTok scheduler."""
    global _SCHEDULER
    if _SCHEDULER is None:
        _SCHEDULER = TikTokScheduler()
    return _SCHEDULER
