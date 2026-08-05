"""Hair generator — hair style/length/color parameters."""
from __future__ import annotations

from typing import Any

_HAIR_LENGTHS = ("short", "medium", "long")
_HAIR_TEXTURES = ("straight", "wavy", "curly", "coily")


class HairGenerator:
    """Generates hair parameters."""

    def generate(self, *, color: str = "#2b2b2b", style: str | None = None,
                 length: str | None = None, seed: int | None = None) -> dict[str, Any]:
        length = length if length in _HAIR_LENGTHS else _HAIR_LENGTHS[(seed or 0) % 3]
        texture = _HAIR_TEXTURES[(seed or 0) % 4]
        return {
            "style": style or f"{length}_{texture}",
            "length": length,
            "texture": texture,
            "color": color,
            "density": 0.8 + ((seed or 0) % 3) * 0.05,
            "shine": 0.3 + ((seed or 0) % 4) * 0.1,
        }


_hair_generator: HairGenerator | None = None


def get_hair_generator() -> HairGenerator:
    global _hair_generator
    if _hair_generator is None:
        _hair_generator = HairGenerator()
    return _hair_generator
