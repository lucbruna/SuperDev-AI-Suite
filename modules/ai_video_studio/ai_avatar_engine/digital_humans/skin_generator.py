"""Skin generator — skin tone palettes with deterministic selection."""
from __future__ import annotations

from typing import Any

_SKIN_TONES = {
    "fair": "#f6d9c4", "light": "#f0c8a0", "medium": "#e8b48c",
    "tan": "#c68642", "brown": "#9c6433", "deep": "#6b4226",
}


class SkinGenerator:
    """Generates skin parameters (tone, undertone, sheen)."""

    def generate(self, *, tone: str | None = None, seed: int | None = None) -> dict[str, Any]:
        if tone is None:
            tone = list(_SKIN_TONES)[(seed or 0) % len(_SKIN_TONES)]
        if tone not in _SKIN_TONES:
            raise ValueError(f"unknown skin tone '{tone}'")
        return {
            "tone": tone,
            "hex": _SKIN_TONES[tone],
            "undertone": "warm" if (seed or 0) % 2 == 0 else "cool",
            "sheen": 0.15 + ((seed or 0) % 10) * 0.02,
        }

    def tones(self) -> list[str]:
        return list(_SKIN_TONES)


_skin_generator: SkinGenerator | None = None


def get_skin_generator() -> SkinGenerator:
    global _skin_generator
    if _skin_generator is None:
        _skin_generator = SkinGenerator()
    return _skin_generator
