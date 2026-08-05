"""Elderly avatars — mature presenter profiles."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile

ELDERLY_AVATARS = [
    AvatarProfile("old_tia", "Tia Rosa", style="realistic", dimension="3d", gender="female",
                  age_group="elderly", voice="tia_f", default_outfit="formal",
                  tags=["story", "history", "wisdom"]),
    AvatarProfile("old_henry", "Henry Wells", style="realistic", dimension="3d", gender="male",
                  age_group="elderly", voice="henry_m", default_outfit="formal",
                  tags=["history", "news"]),
    AvatarProfile("old_min", "Gran", style="minimalist", dimension="2d", gender="female",
                  age_group="elderly", voice="gran_f", default_outfit="casual",
                  tags=["story", "calm"]),
]


def avatars() -> list[AvatarProfile]:
    return ELDERLY_AVATARS
