"""Generation cache — keyed result caching to avoid duplicate work."""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any


class GenerationCache:
    """LRU-ish in-memory cache keyed by a hash of (mode, prompt, params)."""

    def __init__(self, max_size: int = 256, ttl_seconds: float = 3600.0) -> None:
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._store: dict[str, tuple[float, Any]] = {}

    @staticmethod
    def _key(mode: str, prompt: str, params: dict[str, Any]) -> str:
        payload = json.dumps([mode, prompt, params], sort_keys=True, default=str)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get(self, *, mode: str, prompt: str, params: dict[str, Any] | None = None) -> Any | None:
        key = self._key(mode, prompt, params or {})
        hit = self._store.get(key)
        if hit is None:
            return None
        timestamp, value = hit
        if time.time() - timestamp > self.ttl_seconds:
            self._store.pop(key, None)
            return None
        return value

    def set(self, *, mode: str, prompt: str, params: dict[str, Any] | None, value: Any) -> str:
        key = self._key(mode, prompt, params or {})
        self._store[key] = (time.time(), value)
        if len(self._store) > self.max_size:
            oldest = min(self._store, key=lambda k: self._store[k][0])
            self._store.pop(oldest, None)
        return key

    def invalidate(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()

    def size(self) -> int:
        return len(self._store)


_generation_cache: GenerationCache | None = None


def get_generation_cache() -> GenerationCache:
    global _generation_cache
    if _generation_cache is None:
        _generation_cache = GenerationCache()
    return _generation_cache
