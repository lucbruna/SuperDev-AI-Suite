from __future__ import annotations

import time
from typing import Any


class CacheEntry:
    """A single entry in the memory cache."""

    def __init__(self, key: str, value: Any, ttl: float | None = None):
        self._key = key
        self._value = value
        self._ttl = ttl
        self._created_at = time.time()
        self._accessed_at = time.time()
        self._access_count = 0

    @property
    def key(self) -> str:
        return self._key

    @property
    def value(self) -> Any:
        self._accessed_at = time.time()
        self._access_count += 1
        return self._value

    @property
    def is_expired(self) -> bool:
        if self._ttl is None:
            return False
        return time.time() > self._created_at + self._ttl

    @property
    def access_count(self) -> int:
        return self._access_count

    @property
    def age(self) -> float:
        return time.time() - self._created_at

    def touch(self) -> None:
        self._accessed_at = time.time()
        self._access_count += 1


class MemoryCache:
    """TTL-based cache with LRU eviction for memory operations."""

    def __init__(self, max_size: int = 10000, default_ttl: float = 60.0):
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._entries: dict[str, CacheEntry] = {}

    @property
    def max_size(self) -> int:
        return self._max_size

    @property
    def default_ttl(self) -> float:
        return self._default_ttl

    @property
    def size(self) -> int:
        return len(self._entries)

    async def get(self, key: str) -> Any | None:
        entry = self._entries.get(key)
        if entry is None:
            return None
        if entry.is_expired:
            del self._entries[key]
            return None
        return entry.value

    async def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        if len(self._entries) >= self._max_size:
            self._evict()
        self._entries[key] = CacheEntry(key, value, ttl or self._default_ttl)

    async def delete(self, key: str) -> bool:
        if key in self._entries:
            del self._entries[key]
            return True
        return False

    async def has(self, key: str) -> bool:
        entry = self._entries.get(key)
        if entry is None:
            return False
        if entry.is_expired:
            del self._entries[key]
            return False
        return True

    async def clear(self) -> None:
        self._entries.clear()

    def _evict(self) -> None:
        if not self._entries:
            return
        expired = [k for k, v in self._entries.items() if v.is_expired]
        if expired:
            for k in expired[:10]:
                del self._entries[k]
            return
        lru = min(self._entries.items(), key=lambda item: item[1]._accessed_at)
        del self._entries[lru[0]]

    async def get_or_set(self, key: str, factory: callable, ttl: float | None = None) -> Any:
        value = await self.get(key)
        if value is not None:
            return value
        value = factory()
        await self.set(key, value, ttl)
        return value

    def invalidate_pattern(self, prefix: str) -> int:
        keys = [k for k in self._entries if k.startswith(prefix)]
        for k in keys:
            del self._entries[k]
        return len(keys)

    def stats(self) -> dict[str, Any]:
        return {
            "size": len(self._entries),
            "max_size": self._max_size,
            "default_ttl": self._default_ttl,
            "utilization": len(self._entries) / self._max_size if self._max_size > 0 else 0,
        }
