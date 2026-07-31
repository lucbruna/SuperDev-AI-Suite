"""Protocol helpers for the DevOps Engine (Volume 37)."""

from __future__ import annotations

import random
import re
import string
import time
from typing import Any, Iterable


def new_id(prefix: str = "item") -> str:
    """Short random id like ``server-a1b2c3d4``."""
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits,
                                    k=8))
    return f"{prefix}-{suffix}"


def coerce_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on", "sim")
    return default


def coerce_number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def round_money(value: Any, digits: int = 2) -> float:
    """Rounds a money value to a fixed number of decimals."""
    return round(coerce_number(value), digits)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


def tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"\w+", (text or "").lower())
            if token]


def safe_get(data: dict[str, Any], path: str, default: Any = None) -> Any:
    current: Any = data
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return default
    return current


def top_n(items: Iterable[Any], key, limit: int = 5) -> list[Any]:
    return sorted(items, key=key, reverse=True)[:max(0, limit)]


def rate(part: float, whole: float) -> float:
    """Returns a 0..1 utilization rate, guarded against zero."""
    if not whole:
        return 0.0
    return max(0.0, min(1.0, float(part) / float(whole)))


def now() -> float:
    return time.time()
