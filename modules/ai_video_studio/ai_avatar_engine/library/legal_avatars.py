"""Legal avatars — legal/law presenter profiles."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile

LEGAL_AVATARS = [
    AvatarProfile("law_attorney", "Attorney Claire Reed", style="realistic", dimension="3d", gender="female",
                  age_group="adult", voice="claire_f", default_outfit="formal",
                  tags=["lawyer", "legal", "authority"]),
    AvatarProfile("law_advocate", "Advocate Marcus Cole", style="realistic", dimension="3d", gender="male",
                  age_group="adult", voice="marcus_m", default_outfit="formal",
                  tags=["lawyer", "legal"]),
    AvatarProfile("law_paralegal", "Nina Delgado", style="realistic", dimension="3d", gender="female",
                  age_group="young", voice="nina_f", default_outfit="business",
                  tags=["paralegal", "legal"]),
]


def avatars() -> list[AvatarProfile]:
    return LEGAL_AVATARS
