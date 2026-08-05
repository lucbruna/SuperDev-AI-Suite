"""Body generator — deterministic body dimensions from build/age/height."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_avatar_engine.digital_humans.body_proportions import (
    get_body_proportions,
)

_BUILD_TABLE = {
    "slim": {"shoulder": 0.42, "chest": 0.52, "waist": 0.44, "hip": 0.50, "mass": 0.8},
    "average": {"shoulder": 0.45, "chest": 0.56, "waist": 0.50, "hip": 0.54, "mass": 1.0},
    "athletic": {"shoulder": 0.48, "chest": 0.60, "waist": 0.46, "hip": 0.54, "mass": 1.15},
    "curvy": {"shoulder": 0.46, "chest": 0.60, "waist": 0.56, "hip": 0.62, "mass": 1.1},
    "tall": {"shoulder": 0.46, "chest": 0.57, "waist": 0.50, "hip": 0.55, "mass": 1.05},
}


class BodyGenerator:
    """Generates normalized body proportion parameters for an avatar."""

    def generate(self, *, build: str = "average", height_cm: int = 172,
                 age_group: str = "adult", seed: int | None = None) -> dict[str, Any]:
        profile = _BUILD_TABLE.get(build, _BUILD_TABLE["average"])
        proportions = get_body_proportions().for_height(height_cm)
        return {
            "build": build,
            "height_cm": height_cm,
            "age_group": age_group,
            "shoulder_ratio": profile["shoulder"],
            "chest_ratio": profile["chest"],
            "waist_ratio": profile["waist"],
            "hip_ratio": profile["hip"],
            "mass_ratio": profile["mass"],
            "proportions": proportions,
            "arm_length_ratio": proportions["arm_length_ratio"],
            "leg_length_ratio": proportions["leg_length_ratio"],
            "head_ratio": proportions["head_ratio"],
        }


_body_generator: BodyGenerator | None = None


def get_body_generator() -> BodyGenerator:
    global _body_generator
    if _body_generator is None:
        _body_generator = BodyGenerator()
    return _body_generator
