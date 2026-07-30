from __future__ import annotations

import asyncio
import time
from typing import Any

from ..database_interfaces import ICacheEngine


class _CacheEntry:
    __slots__ = ("value", "expires_at")

    def __init__(self, value: Any, ttl: int | None = None) -> None:
        self.value = value
        self.expires_at = (time.monotonic() + ttl) if ttl is not None else None


class MemoryCacheEngine(ICacheEngine):
    """Simple in-memory cache engine.

    Useful for development, testing, or lightweight caching without Redis.
    """

    def __init__(self) -> None:
        self._store: dict[str, _CacheEntry] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any:
        async with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if entry.expires_at is not None and time.monotonic() >= entry.expires_at:
                del self._store[key]
                return None
            return entry.value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        async with self._lock:
            self._store[key] = _CacheEntry(value, ttl)

    async def delete(self, key: str) -> bool:
        async with self._lock:
            existed = key in self._store
            self._store.pop(key, None)
            return existed

    async def clear(self) -> None:
        async with self._lock:
            self._store.clear()

    async def exists(self, key: str) -> bool:
        async with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return False
            if entry.expires_at is not None and time.monotonic() >= entry.expires_at:
                del self._store[key]
                return False
            return True

    async def size(self) -> int:
        async with self._lock:
            return len(self._store)


__all__ = [
    "MemoryCacheEngine",
]
