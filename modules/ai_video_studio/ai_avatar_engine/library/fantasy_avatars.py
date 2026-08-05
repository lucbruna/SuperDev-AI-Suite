"""Fantasy avatars — fantasy-world presenter profiles."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile

FANTASY_AVATARS = [
    AvatarProfile("fan_elf", "Elara Swiftleaf", style="anime", dimension="2d", gender="female",
                  age_group="young", voice="elara_f", default_outfit="creative",
                  tags=["fantasy", "elf", "story"]),
    AvatarProfile("fan_wizard", "Mordecai", style="3d", dimension="3d", gender="male",
                  age_group="elderly", voice="mordecai_m", default_outfit="formal",
                  tags=["fantasy", "wizard", "magic"]),
    AvatarProfile("fan_knight", "Ser Brynn", style="realistic", dimension="3d", gender="female",
                  age_group="adult", voice="brynn_f", default_outfit="formal",
                  tags=["fantasy", "knight", "hero"]),
]


def avatars() -> list[AvatarProfile]:
    return FANTASY_AVATARS
