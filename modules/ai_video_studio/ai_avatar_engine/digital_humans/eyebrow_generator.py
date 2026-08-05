"""Eyebrow generator — brow shape/thickness/color parameters."""
from __future__ import annotations

from typing import Any

_BROW_STYLES = ("straight", "arched", "angled", "soft")


class EyebrowGenerator:
    """Generates eyebrow parameters."""

    def generate(self, *, style: str | None = None, hair_color: str = "#2b2b2b",
                 seed: int | None = None) -> dict[str, Any]:
        style = style if style in _BROW_STYLES else _BROW_STYLES[(seed or 0) % len(_BROW_STYLES)]
        return {
            "style": style,
            "thickness": 0.4 + ((seed or 0) % 4) * 0.1,
            "density": 0.7 + ((seed or 0) % 3) * 0.1,
            "color": hair_color,
            "arch_height": 0.3 if style == "arched" else (0.5 if style == "angled" else 0.2),
        }


_eyebrow_generator: EyebrowGenerator | None = None


def get_eyebrow_generator() -> EyebrowGenerator:
    global _eyebrow_generator
    if _eyebrow_generator is None:
        _eyebrow_generator = EyebrowGenerator()
    return _eyebrow_generator
