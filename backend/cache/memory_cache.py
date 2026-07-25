from __future__ import annotations

import time
from typing import Any


class MemoryCache:
    """In-memory cache with TTL support."""

    def __init__(self, max_size: int = 10000):
        self._store: dict[str, tuple[Any, float | None]] = {}
        self._max_size = max_size

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if expires_at and time.time() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        if len(self._store) >= self._max_size:
            oldest_key = next(iter(self._store))
            del self._store[oldest_key]
        expires_at = time.time() + ttl if ttl else None
        self._store[key] = (value, expires_at)

    def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False

    def clear(self) -> None:
        self._store.clear()

    def size(self) -> int:
        return len(self._store)
