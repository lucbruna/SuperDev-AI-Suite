"""Color engine — hair color application and natural variation."""
from __future__ import annotations

from typing import Any

_HAIR_COLORS = {
    "black": "#1a1a1a", "dark_brown": "#3a2a1a", "brown": "#5a3a20",
    "chestnut": "#8a4b2a", "blonde": "#d9b36a", "platinum": "#e8e0c8",
    "red": "#b04030", "auburn": "#7a3a20", "grey": "#b8b8b8", "white": "#f0f0f0",
}


class ColorEngine:
    """Resolves hair color names to hex values with natural variation."""

    def resolve(self, color: str) -> dict[str, Any]:
        if color in _HAIR_COLORS:
            return {"name": color, "hex": _HAIR_COLORS[color]}
        if color.startswith("#") and len(color) == 7:
            return {"name": "custom", "hex": color}
        raise KeyError(f"unknown hair color '{color}'")

    def colors(self) -> list[str]:
        return list(_HAIR_COLORS)


_color_engine: ColorEngine | None = None


def get_color_engine() -> ColorEngine:
    global _color_engine
    if _color_engine is None:
        _color_engine = ColorEngine()
    return _color_engine
