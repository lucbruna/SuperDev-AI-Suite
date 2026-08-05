"""Beard generator — facial-hair parameters."""
from __future__ import annotations

from typing import Any

_BEARD_STYLES = ("none", "stubble", "goatee", "full", "mustache_only")


class BeardGenerator:
    """Generates beard parameters."""

    def generate(self, *, style: str | None = None, color: str = "#2b2b2b",
                 seed: int | None = None) -> dict[str, Any]:
        style = style if style in _BEARD_STYLES else _BEARD_STYLES[(seed or 0) % len(_BEARD_STYLES)]
        return {
            "style": style,
            "color": color,
            "length": 0.2 if style == "stubble" else (0.6 if style == "full" else 0.3),
            "density": 0.5 + ((seed or 0) % 4) * 0.1,
            "coverage": 0.0 if style == "none" else 0.6 + ((seed or 0) % 3) * 0.1,
        }


_beard_generator: BeardGenerator | None = None


def get_beard_generator() -> BeardGenerator:
    global _beard_generator
    if _beard_generator is None:
        _beard_generator = BeardGenerator()
    return _beard_generator
