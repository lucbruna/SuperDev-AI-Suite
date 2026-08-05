"""Glasses generator — eyewear parameters."""
from __future__ import annotations

from typing import Any

_STYLES = ("none", "round", "square", "wayfarer", "reading", "sport")


class GlassesGenerator:
    """Generates eyewear parameters."""

    def generate(self, *, style: str | None = None, occasion: str = "business",
                 seed: int | None = None) -> dict[str, Any]:
        style = style if style in _STYLES else (
            "round" if occasion == "creative" else
            "sport" if occasion == "sport" else "square")
        return {
            "type": style,
            "frame_color": "#222222" if (seed or 0) % 2 == 0 else "#8a6a3a",
            "lens": "clear",
            "present": style != "none",
        }

    def styles(self) -> list[str]:
        return list(_STYLES)


_glasses_generator: GlassesGenerator | None = None


def get_glasses_generator() -> GlassesGenerator:
    global _glasses_generator
    if _glasses_generator is None:
        _glasses_generator = GlassesGenerator()
    return _glasses_generator
