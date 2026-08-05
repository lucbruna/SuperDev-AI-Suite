"""Color palettes — curated clothing color palettes by occasion."""
from __future__ import annotations


PALETTES: dict[str, list[str]] = {
    "business": ["#2c3e50", "#34495e", "#7f8c8d", "#bdc3c7"],
    "formal": ["#1a1a2e", "#2d2d44", "#c9a86a", "#f0e6d2"],
    "casual": ["#5b8db8", "#e8d5a3", "#d97777", "#f0e6d2"],
    "tech": ["#1f2833", "#45a29e", "#66fcf1", "#c5c6c7"],
    "sport": ["#d9534f", "#f5f5f5", "#2b3a55", "#ffd166"],
    "creative": ["#7b4b94", "#f2c14e", "#2ec4b6", "#e71d36"],
    "minimal": ["#404040", "#e0e0e0", "#8a8a8a", "#1a1a1a"],
    "medical": ["#e8f0fe", "#4a90d9", "#ffffff", "#1e3a5f"],
    "agriculture": ["#5a7d3a", "#8fb339", "#e8d5a3", "#3d550c"],
}


class ColorPalettes:
    """Provides color palettes for garment selection."""

    def get(self, occasion: str) -> list[str]:
        return list(PALETTES.get(occasion, PALETTES["casual"]))

    def occasions(self) -> list[str]:
        return list(PALETTES)


_color_palettes: ColorPalettes | None = None


def get_color_palettes() -> ColorPalettes:
    global _color_palettes
    if _color_palettes is None:
        _color_palettes = ColorPalettes()
    return _color_palettes
