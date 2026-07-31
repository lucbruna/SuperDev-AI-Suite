"""Cache engine."""
from __future__ import annotations
from typing import Any, Dict, Optional
import time

class CacheEngine:
    def __init__(self, max_size: int = 1000, ttl: int = 300) -> None:
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_size = max_size
        self._ttl = ttl
        self._hits = 0
        self._misses = 0
    def get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if not entry:
            self._misses += 1
            return None
        if time.time() - entry["created_at"] > self._ttl:
            del self._cache[key]
            self._misses += 1
            return None
        self._hits += 1
        entry["access_count"] += 1
        entry["last_accessed"] = time.time()
        return entry["value"]
    def set(self, key: str, value: Any, ttl: int = None) -> Dict[str, Any]:
        if len(self._cache) >= self._max_size:
            oldest = min(self._cache, key=lambda k: self._cache[k].get("last_accessed", 0))
            del self._cache[oldest]
        entry = {"value": value, "created_at": time.time(), "ttl": ttl or self._ttl, "access_count": 0}
        self._cache[key] = entry
        return {"key": key, "stored": True}
    def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    def clear(self) -> int:
        n = len(self._cache)
        self._cache.clear()
        return n
    def stats(self) -> Dict[str, Any]:
        total = self._hits + self._misses
        return {"hits": self._hits, "misses": self._misses, "hit_rate": (self._hits / total * 100) if total > 0 else 0, "size": len(self._cache), "max_size": self._max_size}
    def exists(self, key: str) -> bool:
        return key in self._cache and time.time() - self._cache[key]["created_at"] <= self._ttl
    def keys(self) -> list:
        return list(self._cache.keys())
    def size(self) -> int:
        return len(self._cache)
