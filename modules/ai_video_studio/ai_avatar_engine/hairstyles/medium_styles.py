"""Medium hairstyles catalog."""
from __future__ import annotations

from typing import Any

MEDIUM_STYLES: list[dict[str, Any]] = [
    {"id": "medium_bob", "length": "medium", "texture": "straight", "volume": 0.4, "cut": "bob"},
    {"id": "medium_lob", "length": "medium", "texture": "wavy", "volume": 0.5, "cut": "lob"},
    {"id": "medium_swept", "length": "medium", "texture": "straight", "volume": 0.3, "cut": "side_swept"},
    {"id": "medium_curly", "length": "medium", "texture": "curly", "volume": 0.7, "cut": "natural"},
    {"id": "medium_shag", "length": "medium", "texture": "wavy", "volume": 0.6, "cut": "shag"},
]


def styles() -> list[dict[str, Any]]:
    return MEDIUM_STYLES
