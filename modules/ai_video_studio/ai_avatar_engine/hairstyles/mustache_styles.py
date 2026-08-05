"""Mustache styles catalog."""
from __future__ import annotations

from typing import Any

MUSTACHE_STYLES: list[dict[str, Any]] = [
    {"id": "mustache_none", "coverage": 0.0, "length": 0.0},
    {"id": "mustache_pencil", "coverage": 0.4, "length": 0.2},
    {"id": "mustache_full", "coverage": 0.8, "length": 0.3},
    {"id": "mustache_handlebar", "coverage": 0.7, "length": 0.5},
    {"id": "mustache_horseshoe", "coverage": 0.6, "length": 0.4},
]


def styles() -> list[dict[str, Any]]:
    return MUSTACHE_STYLES
