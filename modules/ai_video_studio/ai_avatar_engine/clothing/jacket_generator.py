"""Jacket generator — jacket/coat garment parameters."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_avatar_engine.clothing.wardrobe_manager import (
    get_wardrobe_manager,
)


class JacketGenerator:
    """Generates jacket parameters from a wardrobe selection."""

    def generate(self, occasion: str = "business", *, seed: int | None = None) -> dict[str, Any]:
        sel = get_wardrobe_manager().select(occasion, seed=seed)
        has_jacket = occasion in ("business", "formal", "creative", "tech")
        return {
            "type": "blazer" if occasion in ("business", "formal") else ("hoodie" if occasion == "casual" else "vest"),
            "color": sel["primary_color"],
            "fabric": sel["fabric"],
            "present": has_jacket,
            "lapels": "notch" if occasion in ("business", "formal") else "none",
        }


_jacket_generator: JacketGenerator | None = None


def get_jacket_generator() -> JacketGenerator:
    global _jacket_generator
    if _jacket_generator is None:
        _jacket_generator = JacketGenerator()
    return _jacket_generator
