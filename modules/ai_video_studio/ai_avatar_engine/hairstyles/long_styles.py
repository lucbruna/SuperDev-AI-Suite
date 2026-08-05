"""Long hairstyles catalog."""
from __future__ import annotations

from typing import Any

LONG_STYLES: list[dict[str, Any]] = [
    {"id": "long_straight", "length": "long", "texture": "straight", "volume": 0.4, "layers": "none"},
    {"id": "long_wavy", "length": "long", "texture": "wavy", "volume": 0.6, "layers": "soft"},
    {"id": "long_curly", "length": "long", "texture": "curly", "volume": 0.8, "layers": "natural"},
    {"id": "long_layered", "length": "long", "texture": "wavy", "volume": 0.5, "layers": "layered"},
    {"id": "long_braids", "length": "long", "texture": "straight", "volume": 0.3, "layers": "braids"},
]


def styles() -> list[dict[str, Any]]:
    return LONG_STYLES
