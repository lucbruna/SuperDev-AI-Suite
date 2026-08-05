"""Livestock Video Generator — video briefs per animal type and topic."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief

_TOPICS: dict[str, str] = {
    "feeding": "balanced feeding and ration management",
    "health": "routine health checks and vaccination schedules",
    "welfare": "animal welfare, comfort and handling",
    "breeding": "reproductive management and breeding windows",
}


class LivestockVideoGenerator:
    """Builds narration scripts for livestock management videos."""

    def generate(self, *, animal: str = "cattle", topic: str = "health",
                 voice: str = "default") -> dict[str, Any]:
        topic = topic if topic in _TOPICS else "health"
        title = f"{animal.title()} {topic} essentials"
        scenes = [
            f"An overview of {animal} {topic} for modern producers.",
            f"Key practices today: {_TOPICS[topic]}.",
            "Track individual animal data and act on outliers.",
            "A healthy herd starts with consistent daily routines.",
            f"Review your {animal} management plan and improve next cycle.",
        ]
        return build_brief("agriculture", title, scenes, voice=voice,
                           animal=animal, topic=topic).to_dict()


_livestock_video_generator: LivestockVideoGenerator | None = None


def get_livestock_video_generator() -> LivestockVideoGenerator:
    global _livestock_video_generator
    if _livestock_video_generator is None:
        _livestock_video_generator = LivestockVideoGenerator()
    return _livestock_video_generator
