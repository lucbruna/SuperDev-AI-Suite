"""Scheduling — generates a production calendar from the plan."""
from __future__ import annotations

from typing import Any


class Scheduling:
    """Creates a day-by-day production schedule."""

    def build(self, plan: dict[str, Any]) -> dict[str, Any]:
        scenes = plan.get("scenes", 1)
        days = max(1, (scenes + 1) // 2)
        return {
            "days": days,
            "scenes_per_day": scenes / days,
            "phases": {
                "pre": days,
                "production": days * 2,
                "post": days,
            },
        }


_scheduling: Scheduling | None = None


def get_scheduling() -> Scheduling:
    global _scheduling
    if _scheduling is None:
        _scheduling = Scheduling()
    return _scheduling
