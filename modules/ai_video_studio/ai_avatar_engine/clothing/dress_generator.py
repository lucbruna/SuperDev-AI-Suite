"""Dress generator — dress garment parameters (formal/female avatars)."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_avatar_engine.clothing.wardrobe_manager import (
    get_wardrobe_manager,
)


class DressGenerator:
    """Generates dress parameters from a wardrobe selection."""

    def generate(self, occasion: str = "formal", *, gender: str = "female",
                 seed: int | None = None) -> dict[str, Any]:
        sel = get_wardrobe_manager().select(occasion, seed=seed)
        return {
            "type": "evening_gown" if occasion == "formal" else "dress",
            "color": sel["primary_color"],
            "fabric": "silk" if occasion == "formal" else "cotton",
            "length": "long" if occasion == "formal" else "knee",
            "applicable": gender == "female",
        }


_dress_generator: DressGenerator | None = None


def get_dress_generator() -> DressGenerator:
    global _dress_generator
    if _dress_generator is None:
        _dress_generator = DressGenerator()
    return _dress_generator
