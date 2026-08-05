"""Crew schedule — assigns crew to days and call times."""
from __future__ import annotations

from typing import Any


class CrewSchedule:
    """Builds a crew call sheet."""

    def build(self, members: list[str], days: int = 1) -> dict[str, Any]:
        return {
            "days": [
                {
                    "day": day + 1,
                    "call": "08:00",
                    "crew": list(members),
                }
                for day in range(days)
            ]
        }


_crew_schedule: CrewSchedule | None = None


def get_crew_schedule() -> CrewSchedule:
    global _crew_schedule
    if _crew_schedule is None:
        _crew_schedule = CrewSchedule()
    return _crew_schedule
