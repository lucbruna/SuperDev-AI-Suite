"""Hat generator — headwear parameters."""
from __future__ import annotations

from typing import Any

_HAT_BY_OCCASION = {
    "sport": "cap", "casual": "beanie", "creative": "beret",
    "agriculture": "straw_hat", "formal": "fedora",
}


class HatGenerator:
    """Generates headwear parameters."""

    def generate(self, occasion: str = "casual", *, seed: int | None = None) -> dict[str, Any]:
        style = _HAT_BY_OCCASION.get(occasion)
        return {
            "type": style or "none",
            "color": "#8a6a3a" if (seed or 0) % 2 == 0 else "#3a3a3a",
            "present": style is not None,
        }


_hat_generator: HatGenerator | None = None


def get_hat_generator() -> HatGenerator:
    global _hat_generator
    if _hat_generator is None:
        _hat_generator = HatGenerator()
    return _hat_generator
