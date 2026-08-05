"""Business avatars — corporate presenter profiles."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile

BUSINESS_AVATARS = [
    AvatarProfile("biz_maya", "Maya Chen", style="realistic", dimension="3d", gender="female",
                  age_group="adult", voice="maya_f", default_outfit="business",
                  tags=["corporate", "host", "finance"]),
    AvatarProfile("biz_noah", "Noah Rivers", style="realistic", dimension="3d", gender="male",
                  age_group="adult", voice="noah_m", default_outfit="business",
                  tags=["corporate", "narrator"]),
    AvatarProfile("biz_aria", "Aria Stone", style="realistic", dimension="3d", gender="female",
                  age_group="young", voice="aria_f", default_outfit="business",
                  tags=["corporate", "analyst"]),
    AvatarProfile("biz_leo", "Leo Vance", style="realistic", dimension="3d", gender="male",
                  age_group="elderly", voice="leo_m", default_outfit="formal",
                  tags=["corporate", "executive"]),
]


def avatars() -> list[AvatarProfile]:
    return BUSINESS_AVATARS
