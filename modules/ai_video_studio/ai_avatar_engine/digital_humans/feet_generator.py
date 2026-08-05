"""Feet generator — foot geometry parameters."""
from __future__ import annotations

from typing import Any


class FeetGenerator:
    """Generates feet parameters."""

    def generate(self, *, height_cm: int = 172, seed: int | None = None) -> dict[str, Any]:
        return {
            "shoe_size": round(36 + (height_cm - 160) * 0.18 + (seed or 0) % 3, 1),
            "width": 0.5,
            "arch": "normal",
            "toe_shape": "rounded",
        }


_feet_generator: FeetGenerator | None = None


def get_feet_generator() -> FeetGenerator:
    global _feet_generator
    if _feet_generator is None:
        _feet_generator = FeetGenerator()
    return _feet_generator
