"""Texture library — texture presets applied to garments."""
from __future__ import annotations

from typing import Any

TEXTURES: dict[str, dict[str, Any]] = {
    "plain": {"pattern": "none", "scale": 0.0},
    "stripes": {"pattern": "vertical", "scale": 0.15},
    "checkered": {"pattern": "grid", "scale": 0.12},
    "herringbone": {"pattern": "diagonal", "scale": 0.2},
    "dots": {"pattern": "dots", "scale": 0.1},
    "textured_knit": {"pattern": "knit", "scale": 0.25},
}


class TextureLibrary:
    """Provides texture presets for garments."""

    def get(self, texture: str) -> dict[str, Any]:
        if texture not in TEXTURES:
            raise KeyError(f"unknown texture '{texture}'")
        return dict(TEXTURES[texture])

    def names(self) -> list[str]:
        return list(TEXTURES)


_texture_library: TextureLibrary | None = None


def get_texture_library() -> TextureLibrary:
    global _texture_library
    if _texture_library is None:
        _texture_library = TextureLibrary()
    return _texture_library
