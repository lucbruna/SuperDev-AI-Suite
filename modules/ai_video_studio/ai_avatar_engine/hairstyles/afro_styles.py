"""Afro hairstyles catalog."""
from __future__ import annotations

from typing import Any

AFRO_STYLES: list[dict[str, Any]] = [
    {"id": "afro_full", "length": "medium", "texture": "coily", "volume": 1.0, "shape": "round"},
    {"id": "afro_tapered", "length": "short", "texture": "coily", "volume": 0.7, "shape": "tapered"},
    {"id": "afro_fade", "length": "short", "texture": "coily", "volume": 0.5, "shape": "fade"},
    {"id": "afro_high_top", "length": "medium", "texture": "coily", "volume": 0.8, "shape": "high_top"},
    {"id": "afro_puffs", "length": "medium", "texture": "coily", "volume": 0.9, "shape": "puffs"},
]


def styles() -> list[dict[str, Any]]:
    return AFRO_STYLES
