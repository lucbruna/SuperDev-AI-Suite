"""Engineering avatars — engineering/tech presenter profiles."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile

ENGINEERING_AVATARS = [
    AvatarProfile("eng_engineer", "Engineer Aisha Khan", style="realistic", dimension="3d", gender="female",
                  age_group="adult", voice="aisha_f", default_outfit="tech",
                  tags=["engineer", "stem", "software"]),
    AvatarProfile("eng_builder", "Builder Tomás Rocha", style="realistic", dimension="3d", gender="male",
                  age_group="adult", voice="tomas_m", default_outfit="casual",
                  tags=["civil", "construction"]),
    AvatarProfile("eng_bot", "Circuit", style="3d", dimension="3d", gender="neutral",
                  age_group="young", voice="circuit_n", default_outfit="tech",
                  tags=["robot", "ai", "tech"]),
]


def avatars() -> list[AvatarProfile]:
    return ENGINEERING_AVATARS
