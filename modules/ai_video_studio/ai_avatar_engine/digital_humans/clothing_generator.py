"""Clothing generator — outfit parameters from the wardrobe."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_avatar_engine.digital_humans.body_generator import (
    get_body_generator,
)


class ClothingGenerator:
    """Generates clothing parameters for a given body/outfit."""

    def generate(self, *, outfit: str = "business", body: dict[str, Any] | None = None,
                 seed: int | None = None) -> dict[str, Any]:
        body = body or get_body_generator().generate()
        return {
            "outfit": outfit,
            "fit": "tailored" if outfit in ("business", "formal") else "relaxed",
            "chest_allowance": round(0.06 + body["chest_ratio"] * 0.05, 3),
            "waist_allowance": round(0.04 + body["waist_ratio"] * 0.04, 3),
            "sleeve_length": "long",
            "layers": 1 if outfit == "casual" else 2,
        }


_clothing_generator: ClothingGenerator | None = None


def get_clothing_generator() -> ClothingGenerator:
    global _clothing_generator
    if _clothing_generator is None:
        _clothing_generator = ClothingGenerator()
    return _clothing_generator
