"""AIOS Cache Memory — TTL key/value cache store.

Exposes the same uniform interface as the other memory stores while
behaving as a fast TTL cache (used for memoization at platform level).
"""

from __future__ import annotations

import threading
import time
import uuid
from typing import Any


class CacheMemory:
    """Thread-safe TTL cache exposed through the memory-store contract."""

    def __init__(self, default_ttl: float = 60.0, max_entries: int = 10_000) -> None:
        self._default_ttl = default_ttl
        self._max = max_entries
        self._store: dict[str, tuple[float, Any]] = {}
        self._hits = 0
        self._misses = 0
        self._lock = threading.Lock()

    def store(self, content: Any, **meta: Any) -> dict[str, Any]:
        key = meta.get("key")
        if key is None:
            key = f"cache-{uuid.uuid4().hex[:10]}"
        ttl = float(meta.get("ttl", self._default_ttl))
        expires = time.time() + ttl
        with self._lock:
            self._store[key] = (expires, content)
            if len(self._store) > self._max:
                oldest = min(self._store, key=lambda k: self._store[k][0])
                del self._store[oldest]
        return {"record_id": key, "key": key, "expires_at": expires}

    def recall(self, query: Any = None, limit: int = 5, **filters: Any) -> list[dict[str, Any]]:
        key = filters.get("key", query)
        if key is not None:
            with self._lock:
                item = self._store.get(str(key))
                if item is None:
                    self._misses += 1
                    return []
                expires, value = item
                if expires < time.time():
                    del self._store[str(key)]
                    self._misses += 1
                    return []
                self._hits += 1
                return [{"key": str(key), "value": value, "expires_at": expires}]
        with self._lock:
            now = time.time()
            results = [
                {"key": k, "value": v, "expires_at": exp}
                for k, (exp, v) in self._store.items()
                if exp >= now
            ][:limit]
            return results

    def forget(self, record_id: str) -> bool:
        with self._lock:
            return self._store.pop(record_id, None) is not None

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "entries": len(self._store),
                "max": self._max,
                "hits": self._hits,
                "misses": self._misses,
            }

    def snapshot(self) -> dict[str, Any]:
        return self.stats()
