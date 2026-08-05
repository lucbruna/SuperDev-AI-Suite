"""Short hairstyles catalog."""
from __future__ import annotations

from typing import Any

SHORT_STYLES: list[dict[str, Any]] = [
    {"id": "short_crop", "length": "short", "texture": "straight", "volume": 0.3, "sides": "tight"},
    {"id": "short_buzz", "length": "short", "texture": "straight", "volume": 0.1, "sides": "buzz"},
    {"id": "short_pixie", "length": "short", "texture": "wavy", "volume": 0.5, "sides": "tapered"},
    {"id": "short_undercut", "length": "short", "texture": "straight", "volume": 0.4, "sides": "undercut"},
    {"id": "short_curly", "length": "short", "texture": "curly", "volume": 0.6, "sides": "natural"},
]


def styles() -> list[dict[str, Any]]:
    return SHORT_STYLES
