"""Pants generator — pants garment parameters."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_avatar_engine.clothing.wardrobe_manager import (
    get_wardrobe_manager,
)


class PantsGenerator:
    """Generates pants parameters from a wardrobe selection."""

    def generate(self, occasion: str = "business", *, seed: int | None = None) -> dict[str, Any]:
        sel = get_wardrobe_manager().select(occasion, seed=seed)
        return {
            "type": "dress_pants" if occasion in ("business", "formal") else "chinos",
            "color": sel["accent_color"],
            "fabric": "wool" if occasion in ("business", "formal") else "cotton",
            "fit": "slim" if occasion in ("business", "tech") else "regular",
            "length": "full",
        }


_pants_generator: PantsGenerator | None = None


def get_pants_generator() -> PantsGenerator:
    global _pants_generator
    if _pants_generator is None:
        _pants_generator = PantsGenerator()
    return _pants_generator
