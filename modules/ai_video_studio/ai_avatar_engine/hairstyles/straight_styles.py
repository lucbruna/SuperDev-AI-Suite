"""Straight hairstyles catalog."""
from __future__ import annotations

from typing import Any

STRAIGHT_STYLES: list[dict[str, Any]] = [
    {"id": "straight_center", "length": "medium", "texture": "straight", "volume": 0.3, "part": "center"},
    {"id": "straight_side", "length": "long", "texture": "straight", "volume": 0.4, "part": "side"},
    {"id": "straight_bob", "length": "medium", "texture": "straight", "volume": 0.3, "part": "center"},
    {"id": "straight_slick", "length": "short", "texture": "straight", "volume": 0.2, "part": "side"},
    {"id": "straight_pony", "length": "long", "texture": "straight", "volume": 0.3, "part": "ponytail"},
]


def styles() -> list[dict[str, Any]]:
    return STRAIGHT_STYLES
