"""Beard styles catalog."""
from __future__ import annotations

from typing import Any

BEARD_STYLES: list[dict[str, Any]] = [
    {"id": "beard_none", "coverage": 0.0, "length": 0.0},
    {"id": "beard_stubble", "coverage": 0.5, "length": 0.1},
    {"id": "beard_short", "coverage": 0.8, "length": 0.3},
    {"id": "beard_full", "coverage": 1.0, "length": 0.5},
    {"id": "beard_goatee", "coverage": 0.3, "length": 0.4},
    {"id": "beard_van_dyke", "coverage": 0.35, "length": 0.4},
]


def styles() -> list[dict[str, Any]]:
    return BEARD_STYLES
