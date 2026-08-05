"""Education avatars — teacher/presenter profiles for education."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile

EDUCATION_AVATARS = [
    AvatarProfile("edu_prof", "Prof. Elena Vale", style="realistic", dimension="3d", gender="female",
                  age_group="adult", voice="elena_f", default_outfit="business",
                  tags=["teacher", "education", "science"]),
    AvatarProfile("edu_tutor", "Mateo Silva", style="realistic", dimension="3d", gender="male",
                  age_group="young", voice="mateo_m", default_outfit="casual",
                  tags=["tutor", "education", "math"]),
    AvatarProfile("edu_cartoon", "Prof. Pickle", style="cartoon", dimension="2d", gender="neutral",
                  age_group="adult", voice="pickle_n", default_outfit="casual",
                  tags=["kids", "education", "fun"]),
]


def avatars() -> list[AvatarProfile]:
    return EDUCATION_AVATARS
