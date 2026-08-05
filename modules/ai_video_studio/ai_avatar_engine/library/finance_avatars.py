"""Finance avatars — finance/economy presenter profiles."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile

FINANCE_AVATARS = [
    AvatarProfile("fin_analyst", "Analyst Yara Nasser", style="realistic", dimension="3d", gender="female",
                  age_group="young", voice="yara_f", default_outfit="business",
                  tags=["finance", "analyst", "markets"]),
    AvatarProfile("fin_economist", "Dr. Owen Marsh", style="realistic", dimension="3d", gender="male",
                  age_group="adult", voice="owen_m", default_outfit="business",
                  tags=["economist", "finance"]),
    AvatarProfile("fin_adviser", "Adviser Ines Costa", style="realistic", dimension="3d", gender="female",
                  age_group="adult", voice="ines_f", default_outfit="formal",
                  tags=["adviser", "investing"]),
]


def avatars() -> list[AvatarProfile]:
    return FINANCE_AVATARS
