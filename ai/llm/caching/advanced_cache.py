from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


class AdvancedCache:
    """LRU cache with TTL, optional disk persistence, and metrics."""

    def __init__(self, max_size: int = 1000, default_ttl: int = 300, persist_path: str = "") -> None:
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._persist_path = persist_path
        self._cache: dict[str, dict[str, Any]] = {}
        self._expiry: dict[str, float] = {}
        self._access_order: list[str] = []
        self._hits = 0
        self._misses = 0

        if persist_path and os.path.exists(persist_path):
            self._load_from_disk()

    async def get(self, key: str) -> dict[str, Any] | None:
        now = time.time()
        if key not in self._cache:
            self._misses += 1
            return None
        if now > self._expiry.get(key, now):
            await self.invalidate(key)
            self._misses += 1
            return None
        self._hits += 1
        self._touch(key)
        return self._cache[key]

    async def set(self, key: str, value: dict[str, Any], ttl: int | None = None) -> None:
        if len(self._cache) >= self._max_size:
            self._evict_lru()
        self._cache[key] = value
        self._expiry[key] = time.time() + (ttl if ttl is not None else self._default_ttl)
        self._touch(key)
        if self._persist_path:
            self._save_to_disk()

    async def invalidate(self, key: str) -> bool:
        self._cache.pop(key, None)
        self._expiry.pop(key, None)
        if key in self._access_order:
            self._access_order.remove(key)
        return True

    async def clear(self) -> None:
        self._cache.clear()
        self._expiry.clear()
        self._access_order.clear()
        self._hits = 0
        self._misses = 0

    def _touch(self, key: str) -> None:
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

    def _evict_lru(self) -> None:
        if self._access_order:
            oldest = self._access_order.pop(0)
            self._cache.pop(oldest, None)
            self._expiry.pop(oldest, None)

    def get_stats(self) -> dict[str, Any]:
        total = self._hits + self._misses
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / total if total > 0 else 0.0,
            "default_ttl": self._default_ttl,
        }

    def _save_to_disk(self) -> None:
        data = {
            "cache": self._cache,
            "expiry": self._expiry,
            "access_order": self._access_order,
        }
        Path(self._persist_path).write_text(json.dumps(data), encoding="utf-8")

    def _load_from_disk(self) -> None:
        try:
            data = json.loads(Path(self._persist_path).read_text(encoding="utf-8"))
            self._cache = data.get("cache", {})
            self._expiry = {k: float(v) for k, v in data.get("expiry", {}).items()}
            self._access_order = data.get("access_order", [])
        except (json.JSONDecodeError, KeyError):
            self._cache.clear()
            self._expiry.clear()
            self._access_order.clear()

    def to_dict(self) -> dict[str, Any]:
        return {
            "stats": self.get_stats(),
            "persist_path": self._persist_path,
            "has_disk_persistence": bool(self._persist_path),
        }
