"""Shirt generator — shirt garment parameters."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_avatar_engine.clothing.wardrobe_manager import (
    get_wardrobe_manager,
)


class ShirtGenerator:
    """Generates shirt parameters from a wardrobe selection."""

    def generate(self, occasion: str = "business", *, seed: int | None = None) -> dict[str, Any]:
        sel = get_wardrobe_manager().select(occasion, seed=seed)
        return {
            "type": "dress_shirt" if occasion in ("business", "formal") else "tee",
            "color": sel["primary_color"],
            "fabric": sel["fabric"],
            "collar": "point" if occasion in ("business", "formal") else "crew",
            "sleeves": "long",
        }


_shirt_generator: ShirtGenerator | None = None


def get_shirt_generator() -> ShirtGenerator:
    global _shirt_generator
    if _shirt_generator is None:
        _shirt_generator = ShirtGenerator()
    return _shirt_generator
