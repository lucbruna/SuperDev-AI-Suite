from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class CacheEntry:
    """A cached embedding with optional TTL."""

    def __init__(self, key: str, value: List[float], ttl: Optional[float] = None):
        self._key = key
        self._value = list(value)
        self._created = time.time()
        self._ttl = ttl

    @property
    def key(self) -> str:
        return self._key

    @property
    def value(self) -> List[float]:
        return list(self._value)

    @property
    def is_expired(self) -> bool:
        if self._ttl is None:
            return False
        return time.time() - self._created > self._ttl


class Cache:
    """Cache layer for vector embeddings with TTL and eviction."""

    def __init__(self, max_size: int = 1000, default_ttl: Optional[float] = None):
        self._entries: Dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._hits: int = 0
        self._misses: int = 0

    @property
    def size(self) -> int:
        return len(self._entries)

    @property
    def hits(self) -> int:
        return self._hits

    @property
    def misses(self) -> int:
        return self._misses

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return self._hits / total

    def get(self, key: str) -> Optional[List[float]]:
        entry = self._entries.get(key)
        if entry is None:
            self._misses += 1
            return None
        if entry.is_expired:
            del self._entries[key]
            self._misses += 1
            return None
        self._hits += 1
        return entry.value

    def set(self, key: str, value: List[float], ttl: Optional[float] = None) -> None:
        if len(self._entries) >= self._max_size:
            self._evict()
        self._entries[key] = CacheEntry(key, value, ttl or self._default_ttl)

    def remove(self, key: str) -> bool:
        return self._entries.pop(key, None) is not None

    def clear(self) -> None:
        self._entries.clear()

    def _evict(self) -> None:
        if not self._entries:
            return
        oldest = min(self._entries.keys(), key=lambda k: self._entries[k]._created)
        del self._entries[oldest]

    def stats(self) -> Dict[str, Any]:
        return {
            "size": self.size,
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self.hit_rate,
        }
