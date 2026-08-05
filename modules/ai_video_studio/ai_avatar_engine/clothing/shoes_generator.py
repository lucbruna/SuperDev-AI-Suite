"""Shoes generator — footwear parameters."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_avatar_engine.clothing.wardrobe_manager import (
    get_wardrobe_manager,
)

_TYPE_BY_OCCASION = {
    "business": "oxford", "formal": "dress_shoe", "casual": "sneaker",
    "tech": "sneaker", "sport": "running", "creative": "boot",
    "minimal": "loafer", "medical": "clog", "agriculture": "boot",
}


class ShoesGenerator:
    """Generates footwear parameters."""

    def generate(self, occasion: str = "business", *, seed: int | None = None) -> dict[str, Any]:
        sel = get_wardrobe_manager().select(occasion, seed=seed)
        return {
            "type": _TYPE_BY_OCCASION.get(occasion, "sneaker"),
            "color": sel["accent_color"],
            "material": "leather" if occasion in ("business", "formal") else "fabric",
            "heel": 0.0 if occasion in ("business", "formal", "sport") else 0.02,
        }


_shoes_generator: ShoesGenerator | None = None


def get_shoes_generator() -> ShoesGenerator:
    global _shoes_generator
    if _shoes_generator is None:
        _shoes_generator = ShoesGenerator()
    return _shoes_generator
