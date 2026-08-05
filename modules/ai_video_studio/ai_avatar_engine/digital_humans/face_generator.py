"""Face generator — deterministic face-shape parameters."""
from __future__ import annotations

from typing import Any

_FACE_SHAPES = ("oval", "round", "square", "heart", "diamond", "oblong")


class FaceGenerator:
    """Generates face geometry parameters (normalized 0..1, deterministically)."""

    def generate(self, *, shape: str | None = None, age_group: str = "adult",
                 seed: int | None = None) -> dict[str, Any]:
        shape = shape if shape in _FACE_SHAPES else _FACE_SHAPES[(seed or 0) % len(_FACE_SHAPES)]
        return {
            "shape": shape,
            "face_width": 0.5,       # relative to head width
            "face_height": 0.62,     # relative to head height
            "jaw_width": 0.42,
            "cheekbone": 0.3,
            "forehead_height": 0.32,
            "chin_point": 0.25,
            "age_group": age_group,
        }


_face_generator: FaceGenerator | None = None


def get_face_generator() -> FaceGenerator:
    global _face_generator
    if _face_generator is None:
        _face_generator = FaceGenerator()
    return _face_generator
