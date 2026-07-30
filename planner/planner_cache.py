from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class PlannerCache:
    """Cache for planner data."""

    def __init__(self):
        self._cache: dict[str, tuple[Any, float]] = {}
        self._default_ttl: float = 300.0

    def get(self, key: str) -> Any | None:
        if key in self._cache:
            value, expires = self._cache[key]
            if datetime.now(UTC).timestamp() < expires:
                return value
            del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        expires = datetime.now(UTC).timestamp() + (ttl or self._default_ttl)
        self._cache[key] = (value, expires)

    def delete(self, key: str) -> None:
        self._cache.pop(key, None)

    def clear(self) -> None:
        self._cache.clear()

    def size(self) -> int:
        return len(self._cache)
