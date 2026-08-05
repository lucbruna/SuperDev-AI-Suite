"""Social Scheduler — optimal post times per social platform (Volume 7)."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

_WINDOWS = {
    "youtube": [(17, 21)],
    "tiktok": [(18, 22)],
    "instagram": [(11, 13), (19, 21)],
    "facebook": [(12, 14), (19, 21)],
    "linkedin": [(8, 10), (12, 13)],
    "x": [(8, 10), (12, 13)],
}


class SocialScheduler:
    """Compute recommended posting slots per platform."""

    def next_slot(self, platform: str, *, days: int = 7) -> dict | None:
        """Find the next recommended hour for a platform within *days*."""
        windows = _WINDOWS.get(platform.lower())
        if not windows:
            return None
        now = datetime.now()
        for delta in range(days * 24):
            candidate = now + timedelta(hours=delta)
            hour = candidate.hour
            for start, end in windows:
                if start <= hour < end:
                    return {
                        "platform": platform.lower(),
                        "iso": candidate.isoformat(),
                        "window": f"{start:02d}:00-{end:02d}:00",
                    }
        return None

    def plan(self, platforms: list[str]) -> dict[str, dict]:
        """Return a posting plan for several platforms."""
        return {
            p.lower(): slot
            for p in platforms
            if (slot := self.next_slot(p)) is not None
        }

    def stats(self) -> dict[str, int]:
        return {"platforms": len(_WINDOWS)}


_SCHEDULER: SocialScheduler | None = None


def get_social_scheduler() -> SocialScheduler:
    """Get the module-level singleton social scheduler."""
    global _SCHEDULER
    if _SCHEDULER is None:
        _SCHEDULER = SocialScheduler()
    return _SCHEDULER
