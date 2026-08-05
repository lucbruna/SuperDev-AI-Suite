"""Agriculture avatars — farming/agronomy presenter profiles."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile

AGRICULTURE_AVATARS = [
    AvatarProfile("agro_farmer", "Farmer Rosa Lima", style="realistic", dimension="3d", gender="female",
                  age_group="adult", voice="rosa_f", default_outfit="agriculture",
                  tags=["farmer", "agronomy", "rural"]),
    AvatarProfile("agro_agronomist", "Agronomist Pedro Cruz", style="realistic", dimension="3d", gender="male",
                  age_group="adult", voice="pedro_m", default_outfit="agriculture",
                  tags=["agronomist", "crops"]),
    AvatarProfile("agro_tech", "João Plantio", style="cartoon", dimension="2d", gender="male",
                  age_group="young", voice="joao_m", default_outfit="casual",
                  tags=["kids", "agriculture", "fun"]),
]


def avatars() -> list[AvatarProfile]:
    return AGRICULTURE_AVATARS
