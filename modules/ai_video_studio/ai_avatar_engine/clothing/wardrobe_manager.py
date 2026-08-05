"""Wardrobe manager — selects coherent outfits for avatars."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_avatar_engine.clothing.color_palettes import (
    get_color_palettes,
)
from modules.ai_video_studio.ai_avatar_engine.clothing.fabric_materials import (
    get_fabric_materials,
)

_OCCASION_FABRICS = {
    "business": "wool", "formal": "silk", "casual": "cotton", "tech": "polyester",
    "sport": "polyester", "creative": "linen", "minimal": "cotton",
    "medical": "cotton", "agriculture": "linen",
}


class WardrobeManager:
    """Selects garment sets for an occasion with fabric/palette choices."""

    def select(self, occasion: str, *, seed: int | None = None) -> dict[str, Any]:
        palette = get_color_palettes().get(occasion)
        fabric = _OCCASION_FABRICS.get(occasion, "cotton")
        color = palette[(seed or 0) % len(palette)]
        return {
            "occasion": occasion,
            "primary_color": color,
            "accent_color": palette[((seed or 0) + 1) % len(palette)],
            "fabric": fabric,
            "fabric_props": get_fabric_materials().get(fabric),
            "layers": 1 if occasion in ("casual", "sport") else 2,
        }

    def occasions(self) -> list[str]:
        return get_color_palettes().occasions()


_wardrobe_manager: WardrobeManager | None = None


def get_wardrobe_manager() -> WardrobeManager:
    global _wardrobe_manager
    if _wardrobe_manager is None:
        _wardrobe_manager = WardrobeManager()
    return _wardrobe_manager
