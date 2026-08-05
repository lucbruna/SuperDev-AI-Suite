"""Publisher Scheduler — best-time-to-post heuristics and recurring schedules (Volume 7)."""
from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Best posting windows per platform (local hour ranges), based on typical
# engagement curves. Used as heuristics when no per-account history exists.
_BEST_WINDOWS: dict[str, list[tuple[int, int]]] = {
    "youtube": [(17, 21)],
    "tiktok": [(18, 22)],
    "instagram": [(11, 13), (19, 21)],
    "facebook": [(12, 14), (19, 21)],
    "linkedin": [(8, 10), (12, 13)],
    "x": [(8, 10), (12, 13)],
}

_WEEKDAY_NAMES = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


class PublisherScheduler:
    """Schedule publish jobs at recommended times across platforms."""

    def __init__(self) -> None:
        self._recurring: dict[str, dict] = {}

    def best_slot(self, platform: str, *, tz_offset_hours: int = 0) -> dict:
        """Return the next recommended publish time for a platform."""
        windows = _BEST_WINDOWS.get(platform.lower(), [(9, 17)])
        now = datetime.now()
        target = now + timedelta(hours=tz_offset_hours)
        day_index = target.weekday()
        for hours_ahead in range(24 * 7):
            candidate = target + timedelta(hours=hours_ahead)
            wd = candidate.weekday()
            hour = candidate.hour + tz_offset_hours
            hour = hour % 24
            for start, end in windows:
                if start <= hour < end:
                    ts = candidate.timestamp()
                    return {
                        "platform": platform.lower(),
                        "timestamp": ts,
                        "iso": datetime.fromtimestamp(ts).isoformat(),
                        "weekday": _WEEKDAY_NAMES[wd],
                        "window": f"{start:02d}:00-{end:02d}:00",
                    }
        raise RuntimeError("No slot found")  # pragma: no cover — loop always exits

    def next_slots(self, platforms: list[str], *, count: int = 3) -> dict[str, list[dict]]:
        """Return recommended slots for several platforms."""
        out: dict[str, list[dict]] = {}
        for platform in platforms:
            slots = []
            seen: set[float] = set()
            for _ in range(count):
                slot = self.best_slot(platform)
                if slot["timestamp"] in seen:
                    break
                seen.add(slot["timestamp"])
                slots.append(slot)
            out[platform.lower()] = slots
        return out

    def create_recurring(self, *, name: str, platforms: list[str], interval_hours: int) -> dict:
        """Register a recurring schedule rule."""
        rule = {
            "name": name,
            "platforms": list(platforms),
            "interval_hours": max(1, int(interval_hours)),
            "created_at": time.time(),
            "last_fire": None,
        }
        self._recurring[name] = rule
        return rule

    def due_recurring(self, *, now: float | None = None) -> list[dict]:
        """Return recurring rules whose interval has elapsed."""
        now = now if now is not None else time.time()
        due = []
        for rule in self._recurring.values():
            if rule["last_fire"] is None or now - rule["last_fire"] >= rule["interval_hours"] * 3600:
                rule["last_fire"] = now
                due.append(rule)
        return due

    def stats(self) -> dict[str, int]:
        return {"recurring_rules": len(self._recurring)}


_SCHEDULER: PublisherScheduler | None = None


def get_publisher_scheduler() -> PublisherScheduler:
    """Get the module-level singleton scheduler."""
    global _SCHEDULER
    if _SCHEDULER is None:
        _SCHEDULER = PublisherScheduler()
    return _SCHEDULER
