from __future__ import annotations

import time
from typing import Any


class CacheState:
    """In-memory cache with TTL support for frontend data."""

    def __init__(self, default_ttl: float = 60.0) -> None:
        self._cache: dict[str, dict[str, Any]] = {}
        self._default_ttl = default_ttl

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        self._cache[key] = {
            "value": value,
            "expires_at": time.time() + (ttl if ttl is not None else self._default_ttl),
        }

    def get(self, key: str, default: Any = None) -> Any:
        entry = self._cache.get(key)
        if entry is None:
            return default
        if time.time() > entry["expires_at"]:
            self._cache.pop(key, None)
            return default
        return entry["value"]

    def delete(self, key: str) -> bool:
        return self._cache.pop(key, None) is not None

    def clear(self) -> None:
        self._cache.clear()

    def prune(self) -> int:
        now = time.time()
        expired = [k for k, v in self._cache.items() if now > v["expires_at"]]
        for key in expired:
            self._cache.pop(key, None)
        return len(expired)

    def size(self) -> int:
        return len(self._cache)

    def snapshot(self) -> dict[str, Any]:
        return {key: entry["value"] for key, entry in self._cache.items()}
