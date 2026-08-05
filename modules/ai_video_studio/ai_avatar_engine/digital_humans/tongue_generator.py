"""Tongue generator — tongue size/color parameters."""
from __future__ import annotations

from typing import Any


class TongueGenerator:
    """Generates tongue parameters."""

    def generate(self, *, seed: int | None = None) -> dict[str, Any]:
        return {
            "color": "#d97777",
            "size": 0.5 + ((seed or 0) % 4) * 0.06,
            "width": 0.4 + ((seed or 0) % 3) * 0.05,
            "texture": "smooth",
        }


_tongue_generator: TongueGenerator | None = None


def get_tongue_generator() -> TongueGenerator:
    global _tongue_generator
    if _tongue_generator is None:
        _tongue_generator = TongueGenerator()
    return _tongue_generator
