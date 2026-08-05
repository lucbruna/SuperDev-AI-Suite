"""Eye generator — iris/sclera colors and eye-shape parameters."""
from __future__ import annotations

from typing import Any

_IRIS_COLORS = ("#3a2a1a", "#2a4a6a", "#4a7a3a", "#5a5a6a", "#8a6a3a", "#2a2a2a")


class EyeGenerator:
    """Generates eye parameters (color, shape, spacing, size)."""

    def generate(self, *, color: str | None = None, seed: int | None = None) -> dict[str, Any]:
        iris = color if color and color.startswith("#") else _IRIS_COLORS[(seed or 0) % len(_IRIS_COLORS)]
        return {
            "iris_color": iris,
            "sclera_color": "#f5f0e8",
            "pupil_color": "#1a1a1a",
            "shape": "almond" if (seed or 0) % 2 == 0 else "round",
            "eye_size": 0.5 + ((seed or 0) % 5) * 0.05,
            "eye_spacing": 0.5,
            "iris_ratio": 0.42,
        }


_eye_generator: EyeGenerator | None = None


def get_eye_generator() -> EyeGenerator:
    global _eye_generator
    if _eye_generator is None:
        _eye_generator = EyeGenerator()
    return _eye_generator
