"""Accessories generator — eyewear, jewelry, headwear parameters."""
from __future__ import annotations

from typing import Any

_ACCESSORY_TYPES = ("none", "glasses", "watch", "necklace", "earrings", "hat", "scarf")


class AccessoriesGenerator:
    """Generates accessory parameters for an avatar."""

    def generate(self, *, accessory: str | None = None, outfit: str = "business",
                 seed: int | None = None) -> dict[str, Any]:
        accessory = accessory if accessory in _ACCESSORY_TYPES else (
            "glasses" if outfit == "tech" else "watch" if outfit == "business" else "none")
        return {
            "type": accessory,
            "metal": "gold" if (seed or 0) % 2 == 0 else "silver",
            "lens": "clear" if accessory == "glasses" else None,
            "frame_color": "#222222" if accessory == "glasses" else None,
        }

    def types(self) -> list[str]:
        return list(_ACCESSORY_TYPES)


_accessories_generator: AccessoriesGenerator | None = None


def get_accessories_generator() -> AccessoriesGenerator:
    global _accessories_generator
    if _accessories_generator is None:
        _accessories_generator = AccessoriesGenerator()
    return _accessories_generator
