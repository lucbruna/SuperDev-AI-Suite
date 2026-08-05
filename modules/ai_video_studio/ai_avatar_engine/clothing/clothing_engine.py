"""Clothing engine — assembles a complete outfit for an avatar."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_avatar_engine.clothing.dress_generator import (
    get_dress_generator,
)
from modules.ai_video_studio.ai_avatar_engine.clothing.glasses_generator import (
    get_glasses_generator,
)
from modules.ai_video_studio.ai_avatar_engine.clothing.hat_generator import (
    get_hat_generator,
)
from modules.ai_video_studio.ai_avatar_engine.clothing.jacket_generator import (
    get_jacket_generator,
)
from modules.ai_video_studio.ai_avatar_engine.clothing.jewelry_generator import (
    get_jewelry_generator,
)
from modules.ai_video_studio.ai_avatar_engine.clothing.pants_generator import (
    get_pants_generator,
)
from modules.ai_video_studio.ai_avatar_engine.clothing.shirt_generator import (
    get_shirt_generator,
)
from modules.ai_video_studio.ai_avatar_engine.clothing.shoes_generator import (
    get_shoes_generator,
)
from modules.ai_video_studio.ai_avatar_engine.clothing.texture_library import (
    get_texture_library,
)
from modules.ai_video_studio.ai_avatar_engine.clothing.wardrobe_manager import (
    get_wardrobe_manager,
)


class ClothingEngine:
    """Composes every garment generator into one complete outfit."""

    def dress(self, *, occasion: str = "business", gender: str = "neutral",
              seed: int | None = None) -> dict[str, Any]:
        selection = get_wardrobe_manager().select(occasion, seed=seed)
        outfit = {
            "occasion": occasion,
            "selection": selection,
            "shirt": get_shirt_generator().generate(occasion, seed=seed),
            "pants": get_pants_generator().generate(occasion, seed=seed),
            "jacket": get_jacket_generator().generate(occasion, seed=seed),
            "shoes": get_shoes_generator().generate(occasion, seed=seed),
            "hat": get_hat_generator().generate(occasion, seed=seed),
            "glasses": get_glasses_generator().generate(occasion=occasion, seed=seed),
            "jewelry": get_jewelry_generator().generate(occasion=occasion, seed=seed),
            "dress": get_dress_generator().generate(occasion, gender=gender, seed=seed),
            "texture": get_texture_library().get("plain"),
        }
        # Dresses replace shirt+pants for female formal avatars.
        if outfit["dress"]["applicable"] and occasion == "formal":
            outfit["shirt"]["present"] = False
            outfit["pants"]["present"] = False
        return outfit

    def occasions(self) -> list[str]:
        return get_wardrobe_manager().occasions()


_clothing_engine: ClothingEngine | None = None


def get_clothing_engine() -> ClothingEngine:
    """Return the shared clothing engine singleton."""
    global _clothing_engine
    if _clothing_engine is None:
        _clothing_engine = ClothingEngine()
    return _clothing_engine
