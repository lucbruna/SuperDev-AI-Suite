"""Sci-fi avatars — futuristic/space presenter profiles."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile

SCIFI_AVATARS = [
    AvatarProfile("sf_android", "Unit-7", style="3d", dimension="3d", gender="neutral",
                  age_group="young", voice="unit7_n", default_outfit="tech",
                  tags=["robot", "android", "future"]),
    AvatarProfile("sf_astronaut", "Cmdr. Vega", style="realistic", dimension="3d", gender="female",
                  age_group="adult", voice="vega_f", default_outfit="tech",
                  tags=["space", "astronaut"]),
    AvatarProfile("sf_hologram", "Holo-Aria", style="pixel_art", dimension="2d", gender="female",
                  age_group="young", voice="holo_f", default_outfit="minimal",
                  tags=["hologram", "ai", "future"]),
]


def avatars() -> list[AvatarProfile]:
    return SCIFI_AVATARS
