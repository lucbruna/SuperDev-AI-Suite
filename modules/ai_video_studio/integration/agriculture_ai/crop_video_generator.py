"""Crop Video Generator — video briefs per crop and growth stage."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief

_STAGES: dict[str, str] = {
    "planting": "sowing and initial germination",
    "growth": "vegetative development and canopy management",
    "flowering": "flowering, pollination and fruit set",
    "harvest": "maturity, harvest windows and post-harvest handling",
}


class CropVideoGenerator:
    """Builds narration scripts for crop management videos."""

    def generate(self, *, crop: str = "soybean", stage: str = "growth",
                 region: str = "brazil", voice: str = "default") -> dict[str, Any]:
        stage = stage if stage in _STAGES else "growth"
        title = f"{crop.title()} {stage} management"
        scenes = [
            f"Welcome to today's guide on {crop} farming in {region}.",
            f"At the {stage} stage, focus on {_STAGES[stage]}.",
            "Monitor soil moisture, nutrients and pest pressure weekly.",
            "Act early on stress signals to protect final yield.",
            f"Apply the recommended practices for {crop} and schedule the next check.",
        ]
        return build_brief("agriculture", title, scenes, voice=voice,
                           crop=crop, stage=stage, region=region).to_dict()


_crop_video_generator: CropVideoGenerator | None = None


def get_crop_video_generator() -> CropVideoGenerator:
    global _crop_video_generator
    if _crop_video_generator is None:
        _crop_video_generator = CropVideoGenerator()
    return _crop_video_generator
