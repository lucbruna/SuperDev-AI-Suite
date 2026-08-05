"""Medical avatars — healthcare presenter profiles."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile

MEDICAL_AVATARS = [
    AvatarProfile("med_doc", "Dr. Amara Obi", style="realistic", dimension="3d", gender="female",
                  age_group="adult", voice="amara_f", default_outfit="medical",
                  tags=["doctor", "health", "trust"]),
    AvatarProfile("med_nurse", "Nurse Theo Klein", style="realistic", dimension="3d", gender="male",
                  age_group="adult", voice="theo_m", default_outfit="medical",
                  tags=["nurse", "health"]),
    AvatarProfile("med_wellness", "Dr. Sofia Paz", style="realistic", dimension="3d", gender="female",
                  age_group="young", voice="sofia_f", default_outfit="medical",
                  tags=["wellness", "nutrition"]),
]


def avatars() -> list[AvatarProfile]:
    return MEDICAL_AVATARS
