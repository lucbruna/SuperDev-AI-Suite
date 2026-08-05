"""Body variations — deterministic body-type variation profiles."""
from __future__ import annotations

from typing import Any

_VARIATIONS = {
    "ectomorph": {"mass_ratio": 0.85, "shoulder_ratio": 0.44, "waist_ratio": 0.42},
    "mesomorph": {"mass_ratio": 1.10, "shoulder_ratio": 0.49, "waist_ratio": 0.46},
    "endomorph": {"mass_ratio": 1.25, "shoulder_ratio": 0.47, "waist_ratio": 0.58},
}


class BodyVariations:
    """Provides somatotype-style body variation profiles."""

    def get(self, variation: str) -> dict[str, Any]:
        if variation not in _VARIATIONS:
            raise KeyError(f"unknown body variation '{variation}'")
        return dict(_VARIATIONS[variation])

    def names(self) -> list[str]:
        return list(_VARIATIONS)


_body_variations: BodyVariations | None = None


def get_body_variations() -> BodyVariations:
    global _body_variations
    if _body_variations is None:
        _body_variations = BodyVariations()
    return _body_variations
