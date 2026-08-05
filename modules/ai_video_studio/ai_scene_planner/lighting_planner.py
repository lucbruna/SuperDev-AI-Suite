"""Lighting planner — suggest lighting setups per scene mood."""
from __future__ import annotations

from typing import Any

LIGHTING_SETUPS = {
    "bright": {"scheme": "high key", "temperature": 5600, "notes": "Even, shadow-free illumination"},
    "warm": {"scheme": "golden hour", "temperature": 3200, "notes": "Low warm sun, soft shadows"},
    "cool": {"scheme": "moonlight", "temperature": 7500, "notes": "Cool blue ambience"},
    "dramatic": {"scheme": "chiaroscuro", "temperature": 4000, "notes": "High contrast, deep shadows"},
    "cozy": {"scheme": "practical", "temperature": 2700, "notes": "Warm practical lamps"},
    "neutral": {"scheme": "studio", "temperature": 5000, "notes": "Balanced three-point setup"},
}


class LightingPlanner:
    """Deterministic lighting plan generation."""

    def plan(self, mood: str = "neutral") -> dict[str, Any]:
        setup = LIGHTING_SETUPS.get(mood, LIGHTING_SETUPS["neutral"])
        return {
            "mood": mood,
            "scheme": setup["scheme"],
            "color_temperature_k": setup["temperature"],
            "key_light": "softbox",
            "fill_light": 0.5,
            "back_light": 0.7,
            "notes": setup["notes"],
        }

    def list_schemes(self) -> list[str]:
        return [f"{mood}: {cfg['scheme']}" for mood, cfg in LIGHTING_SETUPS.items()]


_lighting_planner: LightingPlanner | None = None


def get_lighting_planner() -> LightingPlanner:
    global _lighting_planner
    if _lighting_planner is None:
        _lighting_planner = LightingPlanner()
    return _lighting_planner
