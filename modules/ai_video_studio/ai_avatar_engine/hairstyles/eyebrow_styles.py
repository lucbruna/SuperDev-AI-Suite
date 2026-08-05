"""Eyebrow styles catalog."""
from __future__ import annotations

from typing import Any

EYEBROW_STYLES: list[dict[str, Any]] = [
    {"id": "brow_straight", "shape": "straight", "thickness": 0.5},
    {"id": "brow_arched", "shape": "arched", "thickness": 0.4},
    {"id": "brow_soft", "shape": "soft", "thickness": 0.4},
    {"id": "brow_angled", "shape": "angled", "thickness": 0.5},
    {"id": "brow_bushy", "shape": "straight", "thickness": 0.8},
]


def styles() -> list[dict[str, Any]]:
    return EYEBROW_STYLES
