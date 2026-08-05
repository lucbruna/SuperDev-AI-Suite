"""Age variations — age-related appearance parameters."""
from __future__ import annotations

from typing import Any

_AGE_PARAMS = {
    "child": {"skin_smoothness": 0.95, "wrinkles": 0.0, "hair_density": 0.9,
              "face_softness": 0.9, "height_scale": 0.7},
    "young": {"skin_smoothness": 0.9, "wrinkles": 0.05, "hair_density": 0.95,
              "face_softness": 0.7, "height_scale": 0.98},
    "adult": {"skin_smoothness": 0.7, "wrinkles": 0.2, "hair_density": 0.8,
              "face_softness": 0.5, "height_scale": 1.0},
    "elderly": {"skin_smoothness": 0.45, "wrinkles": 0.6, "hair_density": 0.5,
                "face_softness": 0.3, "height_scale": 0.96},
}


class AgeVariations:
    """Returns age-group appearance parameters."""

    def get(self, age_group: str) -> dict[str, Any]:
        if age_group not in _AGE_PARAMS:
            raise KeyError(f"unknown age group '{age_group}'")
        return dict(_AGE_PARAMS[age_group])

    def groups(self) -> list[str]:
        return list(_AGE_PARAMS)


_age_variations: AgeVariations | None = None


def get_age_variations() -> AgeVariations:
    global _age_variations
    if _age_variations is None:
        _age_variations = AgeVariations()
    return _age_variations
