"""Ecommerce avatars — shopping/product presenter profiles."""
from __future__ import annotations

from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile

ECOMMERCE_AVATARS = [
    AvatarProfile("shop_host", "Host Gemma Ricci", style="realistic", dimension="3d", gender="female",
                  age_group="young", voice="gemma_f", default_outfit="creative",
                  tags=["ecommerce", "sales", "product"]),
    AvatarProfile("shop_reviewer", "Reviewer Sam Okafor", style="realistic", dimension="3d", gender="male",
                  age_group="adult", voice="sam_m", default_outfit="casual",
                  tags=["reviews", "unboxing"]),
    AvatarProfile("shop_cartoon", "Cart Buddy", style="cartoon", dimension="2d", gender="neutral",
                  age_group="young", voice="buddy_n", default_outfit="casual",
                  tags=["kids", "shopping", "fun"]),
]


def avatars() -> list[AvatarProfile]:
    return ECOMMERCE_AVATARS
