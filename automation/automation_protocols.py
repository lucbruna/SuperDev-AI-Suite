"""Protocol helpers shared by automation subsystems."""

from __future__ import annotations

import uuid
from typing import Any, Protocol


class Runnable(Protocol):
    """Anything that can be run."""

    def run(self, *args: Any, **kwargs: Any) -> Any: ...


class Comparable(Protocol):
    """Anything with an ordering key."""

    def key(self) -> Any: ...


def new_id(prefix: str) -> str:
    """Generates a prefixed unique identifier."""
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def safe_get(data: dict[str, Any], key: str, default: Any = None) -> Any:
    """Dot-path aware lookup: 'a.b.c' walks nested dicts."""
    value: Any = data
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            return default
        value = value[part]
    return value


def coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"true", "1", "yes", "sim", "on"}


def coerce_number(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value).replace(",", ".").strip())
