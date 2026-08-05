"""AIOS Cache Service — TTL key/value cache with stats."""

from __future__ import annotations

import threading
import time
from typing import Any


class CacheService:
    """Thread-safe TTL cache service."""

    def __init__(self, default_ttl: float = 60.0, max_entries: int = 10_000) -> None:
        self.default_ttl = default_ttl
        self.max_entries = max_entries
        self._store: dict[str, tuple[float, Any]] = {}
        self._hits = 0
        self._misses = 0
        self._lock = threading.Lock()

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        expires = time.time() + (self.default_ttl if ttl is None else ttl)
        with self._lock:
            self._store[key] = (expires, value)
            if len(self._store) > self.max_entries:
                oldest = min(self._store, key=lambda k: self._store[k][0])
                del self._store[oldest]

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            item = self._store.get(key)
            if item is None:
                self._misses += 1
                return default
            expires, value = item
            if expires < time.time():
                del self._store[key]
                self._misses += 1
                return default
            self._hits += 1
            return value

    def delete(self, key: str) -> bool:
        with self._lock:
            return self._store.pop(key, None) is not None

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "entries": len(self._store),
                "max_entries": self.max_entries,
                "hits": self._hits,
                "misses": self._misses,
                "hit_ratio": round(self._hits / (self._hits + self._misses), 4)
                if (self._hits + self._misses) > 0
                else None,
            }
