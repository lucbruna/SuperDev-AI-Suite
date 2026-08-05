"""Child avatars — children's-content presenter profiles."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile

CHILD_AVATARS = [
    AvatarProfile("child_leo", "Leo", style="cartoon", dimension="2d", gender="male",
                  age_group="child", voice="leo_child", default_outfit="casual",
                  tags=["kids", "stories", "fun"]),
    AvatarProfile("child_mei", "Mei", style="anime", dimension="2d", gender="female",
                  age_group="child", voice="mei_child", default_outfit="casual",
                  tags=["kids", "school", "fun"]),
    AvatarProfile("child_pip", "Pip the Puppy", style="cartoon", dimension="2d", gender="neutral",
                  age_group="child", voice="pip_child", default_outfit="casual",
                  tags=["kids", "animals", "fun"]),
]


def avatars() -> list[AvatarProfile]:
    return CHILD_AVATARS
