"""Teeth generator — tooth geometry and whiteness parameters."""
from __future__ import annotations

from typing import Any


class TeethGenerator:
    """Generates teeth parameters."""

    def generate(self, *, seed: int | None = None) -> dict[str, Any]:
        return {
            "whiteness": 0.6 + ((seed or 0) % 5) * 0.07,
            "alignment": 0.7 + ((seed or 0) % 3) * 0.08,
            "upper_visible": 0.5,
            "lower_visible": 0.2,
            "shape": "rounded" if (seed or 0) % 2 == 0 else "square",
        }


_teeth_generator: TeethGenerator | None = None


def get_teeth_generator() -> TeethGenerator:
    global _teeth_generator
    if _teeth_generator is None:
        _teeth_generator = TeethGenerator()
    return _teeth_generator
