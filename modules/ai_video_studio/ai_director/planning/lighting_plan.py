"""Lighting plan — designs lighting setups per scene."""
from __future__ import annotations

from typing import Any

SETUPS = ["key+fill", "three_point", "natural", "low_key", "high_key"]


class LightingPlan:
    """Creates a lighting plan."""

    def build(self, scenes: int = 1) -> dict[str, Any]:
        return {
            "setups": SETUPS,
            "scene_plan": [{"scene": i + 1, "setup": SETUPS[i % len(SETUPS)]} for i in range(scenes)],
        }


_lighting_plan: LightingPlan | None = None


def get_lighting_plan() -> LightingPlan:
    global _lighting_plan
    if _lighting_plan is None:
        _lighting_plan = LightingPlan()
    return _lighting_plan
