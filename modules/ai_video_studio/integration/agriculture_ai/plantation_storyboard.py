"""Plantation Storyboard — scene-by-scene plan for plantation videos."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief


class PlantationStoryboard:
    """Turns a plantation campaign brief into a scene storyboard."""

    def build(self, *, crop: str = "coffee", area_ha: float = 120.0,
              seasons: list[str] | None = None, voice: str = "default") -> dict[str, Any]:
        seasons = [s for s in (seasons or ["planting", "maintenance", "harvest"]) if s]
        title = f"{crop.title()} plantation storyboard ({area_ha:g} ha)"
        scenes = [
            f"Opening: the {crop} plantation at {area_ha:g} hectares.",
            *[f"Season '{s}': key operations, timing and targets." for s in seasons],
            "Visual summary: expected growth curve and milestones.",
            "Closing call-to-action: consult the agronomist's checklist.",
        ]
        return build_brief("agriculture", title, scenes, voice=voice,
                           crop=crop, area_ha=area_ha, seasons=seasons).to_dict()


_plantation_storyboard: PlantationStoryboard | None = None


def get_plantation_storyboard() -> PlantationStoryboard:
    global _plantation_storyboard
    if _plantation_storyboard is None:
        _plantation_storyboard = PlantationStoryboard()
    return _plantation_storyboard
