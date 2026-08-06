"""Deterministic utility helpers (no clock/network/random)."""
from __future__ import annotations

import hashlib
import json


def stable_hash(*parts: object) -> str:
    """Content-addressed SHA-256 hex digest over serializable parts."""
    payload = json.dumps(parts, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def pct(value: float) -> float:
    return round(clamp(value) * 100, 2)


def ensure_list(value: object) -> list[object]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]
