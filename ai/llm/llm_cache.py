from __future__ import annotations

import time
from typing import Any

from .llm_interfaces import ILLMCache


class LLMCache(ILLMCache):
    """In-memory cache for LLM responses."""

    def __init__(self, default_ttl: int = 300) -> None:
        self._default_ttl = default_ttl
        self._cache: dict[str, dict[str, Any]] = {}
        self._expiry: dict[str, float] = {}

    async def get(self, key: str) -> dict[str, Any] | None:
        if key not in self._cache:
            return None
        if time.time() > self._expiry.get(key, 0):
            await self.invalidate(key)
            return None
        return self._cache.get(key)

    async def set(self, key: str, value: dict[str, Any], ttl: int | None = None) -> None:
        self._cache[key] = value
        self._expiry[key] = time.time() + (ttl if ttl is not None else self._default_ttl)

    async def invalidate(self, key: str) -> bool:
        self._cache.pop(key, None)
        self._expiry.pop(key, None)
        return True

    async def clear(self) -> None:
        self._cache.clear()
        self._expiry.clear()

    @property
    def size(self) -> int:
        now = time.time()
        return sum(1 for e in self._expiry.values() if e > now)

    @property
    def keys(self) -> list[str]:
        now = time.time()
        return [k for k, e in self._expiry.items() if e > now]

    def to_dict(self) -> dict[str, Any]:
        return {
            "size": self.size,
            "keys": self.keys,
            "default_ttl": self._default_ttl,
        }
