"""Influencer avatars — social media influencer profiles."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile

INFLUENCER_AVATARS = [
    AvatarProfile("inf_eve", "Eve Marlow", style="realistic", dimension="3d", gender="female",
                  age_group="young", voice="eve_f", default_outfit="casual",
                  tags=["lifestyle", "social", "influencer"]),
    AvatarProfile("inf_luna", "Luna Moon", style="anime", dimension="2d", gender="female",
                  age_group="young", voice="luna_f", default_outfit="casual",
                  tags=["gaming", "influencer", "youth"]),
    AvatarProfile("inf_kai", "Kai Storm", style="3d", dimension="3d", gender="male",
                  age_group="young", voice="kai_m", default_outfit="sport",
                  tags=["sports", "fitness", "influencer"]),
]


def avatars() -> list[AvatarProfile]:
    return INFLUENCER_AVATARS
