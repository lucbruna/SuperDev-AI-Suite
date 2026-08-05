"""Drone Video Generator — aerial survey video briefs."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief


class DroneVideoGenerator:
    """Builds narration scripts for aerial drone surveys."""

    def generate(self, *, field: str = "north_field", mission: str = "scouting",
                 voice: str = "default") -> dict[str, Any]:
        title = f"Drone survey — {field}"
        scenes = [
            f"Starting the {mission} mission over {field}.",
            "The drone captures high-resolution imagery in transect lines.",
            "Multispectral data reveals stress zones invisible to the eye.",
            "Analysis flags areas needing irrigation, nutrients or pest control.",
            f"Survey complete — review the {field} report and plan action.",
        ]
        return build_brief("agriculture", title, scenes, voice=voice,
                           field=field, mission=mission).to_dict()


_drone_video_generator: DroneVideoGenerator | None = None


def get_drone_video_generator() -> DroneVideoGenerator:
    global _drone_video_generator
    if _drone_video_generator is None:
        _drone_video_generator = DroneVideoGenerator()
    return _drone_video_generator
