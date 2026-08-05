"""Sound plan — plans audio capture and design."""
from __future__ import annotations

from typing import Any


class SoundPlan:
    """Creates a sound production plan."""

    def build(self, scenes: int = 1) -> dict[str, Any]:
        return {
            "capture": "boom + lavaliere",
            "ambience": "recorded on location",
            "music": "licensed library",
            "scene_plan": [{"scene": i + 1, "priority": "dialogue"} for i in range(scenes)],
        }


_sound_plan: SoundPlan | None = None


def get_sound_plan() -> SoundPlan:
    global _sound_plan
    if _sound_plan is None:
        _sound_plan = SoundPlan()
    return _sound_plan
