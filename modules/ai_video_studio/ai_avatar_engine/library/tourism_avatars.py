"""Tourism avatars — travel/tourism presenter profiles."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile

TOURISM_AVATARS = [
    AvatarProfile("tour_guide", "Guide Lina Ferrero", style="realistic", dimension="3d", gender="female",
                  age_group="young", voice="lina_f", default_outfit="casual",
                  tags=["travel", "guide", "adventure"]),
    AvatarProfile("tour_host", "Host Diego Mendez", style="realistic", dimension="3d", gender="male",
                  age_group="adult", voice="diego_m", default_outfit="casual",
                  tags=["travel", "host"]),
    AvatarProfile("tour_cartoon", "Captain Compass", style="cartoon", dimension="2d", gender="neutral",
                  age_group="young", voice="compass_n", default_outfit="casual",
                  tags=["kids", "travel", "fun"]),
]


def avatars() -> list[AvatarProfile]:
    return TOURISM_AVATARS
