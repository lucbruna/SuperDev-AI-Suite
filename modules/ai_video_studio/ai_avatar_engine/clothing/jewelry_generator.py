"""Jewelry generator — jewelry/accessory parameters."""
from __future__ import annotations

from typing import Any

_TYPES = ("none", "watch", "necklace", "earrings", "bracelet", "ring")


class JewelryGenerator:
    """Generates jewelry parameters."""

    def generate(self, *, kind: str | None = None, occasion: str = "business",
                 seed: int | None = None) -> dict[str, Any]:
        kind = kind if kind in _TYPES else (
            "watch" if occasion in ("business", "formal", "tech") else "none")
        return {
            "type": kind,
            "metal": "gold" if (seed or 0) % 2 == 0 else "silver",
            "present": kind != "none",
        }

    def types(self) -> list[str]:
        return list(_TYPES)


_jewelry_generator: JewelryGenerator | None = None


def get_jewelry_generator() -> JewelryGenerator:
    global _jewelry_generator
    if _jewelry_generator is None:
        _jewelry_generator = JewelryGenerator()
    return _jewelry_generator
