"""Eyelash generator — lash length/density/curl parameters."""
from __future__ import annotations

from typing import Any


class EyelashGenerator:
    """Generates eyelash parameters."""

    def generate(self, *, seed: int | None = None, gender: str = "neutral") -> dict[str, Any]:
        intensity = 0.8 if gender == "female" else (0.6 if gender == "male" else 0.7)
        return {
            "length": 0.5 + ((seed or 0) % 4) * 0.1,
            "density": round(intensity * (0.6 + ((seed or 0) % 3) * 0.1), 3),
            "curl": 0.3 + ((seed or 0) % 5) * 0.1,
            "color": "#1a1a1a",
        }


_eyelash_generator: EyelashGenerator | None = None


def get_eyelash_generator() -> EyelashGenerator:
    global _eyelash_generator
    if _eyelash_generator is None:
        _eyelash_generator = EyelashGenerator()
    return _eyelash_generator
