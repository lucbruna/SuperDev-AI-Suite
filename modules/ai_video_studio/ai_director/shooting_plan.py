"""Shooting plan — builds a shot list from the production plan."""
from __future__ import annotations

from typing import Any

SHOT_TYPES = ["wide", "medium", "closeup", "insert"]


class ShootingPlan:
    """Generates a shot list with coverage strategy."""

    def build(self, plan: dict[str, Any]) -> dict[str, Any]:
        scenes = plan.get("scenes", 1)
        shots: list[dict[str, Any]] = []
        for index in range(scenes):
            shots.append(
                {
                    "scene": index + 1,
                    "shot_type": SHOT_TYPES[index % len(SHOT_TYPES)],
                    "duration": round(plan.get("duration", 60.0) / scenes, 2),
                }
            )
        return {"shots": shots, "count": len(shots)}


_shooting_plan: ShootingPlan | None = None


def get_shooting_plan() -> ShootingPlan:
    global _shooting_plan
    if _shooting_plan is None:
        _shooting_plan = ShootingPlan()
    return _shooting_plan
