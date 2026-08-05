"""Texture library — reusable PBR texture assets."""
from __future__ import annotations

from typing import Any


class TextureLibrary:
    """Catalogues texture assets with material types."""

    def __init__(self) -> None:
        self._textures: dict[str, dict[str, Any]] = {}

    def register(self, name: str, *, ref: str, texture_type: str = "albedo", maps: list[str] | None = None) -> None:
        self._textures[name] = {
            "name": name,
            "ref": ref,
            "type": texture_type,
            "maps": maps or ["albedo", "normal"],
        }

    def get(self, name: str) -> dict[str, Any] | None:
        return dict(self._textures[name]) if name in self._textures else None

    def names(self) -> list[str]:
        return list(self._textures.keys())
