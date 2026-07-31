"""Response cache."""
from __future__ import annotations

import hashlib
import time
from typing import Any


class ResponseCache:
    def __init__(self, max_size: int = 500, ttl: int = 600) -> None:
        self._cache: dict[str, dict[str, Any]] = {}
        self._max_size = max_size
        self._ttl = ttl
    def _make_key(self, prompt: str, model: str, params: dict[str, Any] = None) -> str:
        content = f"{prompt}:{model}:{params}"
        return hashlib.sha256(content.encode()).hexdigest()
    def get(self, prompt: str, model: str, params: dict[str, Any] = None) -> dict[str, Any] | None:
        key = self._make_key(prompt, model, params)
        entry = self._cache.get(key)
        if not entry:
            return None
        if time.time() - entry["created_at"] > self._ttl:
            del self._cache[key]
            return None
        entry["access_count"] += 1
        return entry["value"]
    def set(self, prompt: str, model: str, response: dict[str, Any], params: dict[str, Any] = None) -> dict[str, Any]:
        key = self._make_key(prompt, model, params)
        if len(self._cache) >= self._max_size:
            oldest = min(self._cache, key=lambda k: self._cache[k].get("access_count", 0))
            del self._cache[oldest]
        self._cache[key] = {"value": response, "created_at": time.time(), "access_count": 0}
        return {"key": key, "cached": True}
    def invalidate(self, model: str = "") -> int:
        if not model:
            n = len(self._cache)
            self._cache.clear()
            return n
        removed = 0
        keys_to_delete = []
        for k, v in self._cache.items():
            if model in str(v.get("value", {})):
                keys_to_delete.append(k)
        for k in keys_to_delete:
            del self._cache[k]
            removed += 1
        return removed
    def list_cached(self) -> list[str]:
        return list(self._cache.keys())
    def count(self) -> int:
        return len(self._cache)
    def clear(self) -> int:
        n = len(self._cache)
        self._cache.clear()
        return n
