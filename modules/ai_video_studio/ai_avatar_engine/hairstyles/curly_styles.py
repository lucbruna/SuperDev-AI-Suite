"""Curly hairstyles catalog."""
from __future__ import annotations

from typing import Any

CURLY_STYLES: list[dict[str, Any]] = [
    {"id": "curly_coils", "length": "medium", "texture": "curly", "volume": 0.9, "curl_type": "coils"},
    {"id": "curly_spiral", "length": "long", "texture": "curly", "volume": 0.8, "curl_type": "spiral"},
    {"id": "curly_loose", "length": "medium", "texture": "wavy", "volume": 0.6, "curl_type": "loose"},
    {"id": "curly_afro_puff", "length": "short", "texture": "coily", "volume": 1.0, "curl_type": "puff"},
    {"id": "curly_shrinkage", "length": "short", "texture": "coily", "volume": 0.8, "curl_type": "tight"},
]


def styles() -> list[dict[str, Any]]:
    return CURLY_STYLES
