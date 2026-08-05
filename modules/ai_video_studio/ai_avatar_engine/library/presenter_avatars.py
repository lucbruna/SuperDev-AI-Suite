"""Presenter avatars — general-purpose presenter profiles."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile

PRESENTER_AVATARS = [
    AvatarProfile("pres_nova", "Nova 3D", style="3d", dimension="3d", gender="female",
                  age_group="adult", voice="nova_f", default_outfit="tech",
                  tags=["product", "futuristic", "presenter"]),
    AvatarProfile("pres_pixel", "Pixel", style="pixel_art", dimension="2d", gender="neutral",
                  age_group="adult", voice="pixel_n", default_outfit="tech",
                  tags=["retro", "game", "presenter"]),
    AvatarProfile("pres_min", "Min", style="minimalist", dimension="2d", gender="neutral",
                  age_group="adult", voice="min_n", default_outfit="minimal",
                  tags=["minimal", "slides", "presenter"]),
    AvatarProfile("pres_harper", "Harper Quinn", style="realistic", dimension="3d", gender="female",
                  age_group="adult", voice="harper_f", default_outfit="business",
                  tags=["news", "presenter"]),
    AvatarProfile("pres_oliver", "Oliver Grey", style="realistic", dimension="3d", gender="male",
                  age_group="adult", voice="oliver_m", default_outfit="business",
                  tags=["news", "presenter"]),
]


def avatars() -> list[AvatarProfile]:
    return PRESENTER_AVATARS
