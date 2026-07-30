from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from typing import Any


class CacheEntry:
    """A cached hypothesis with expiry."""

    def __init__(self, value: Any, ttl_seconds: int = 300):
        self.value = value
        self.expires_at = datetime.now() + timedelta(seconds=ttl_seconds)

    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at


class HypothesisCache:
    """Cache for generated hypotheses."""

    def __init__(self) -> None:
        self._cache: dict[str, CacheEntry] = {}

    def _make_key(self, context: dict[str, Any]) -> str:
        raw = json.dumps(context, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()

    async def get(self, context: dict[str, Any]) -> Any | None:
        key = self._make_key(context)
        entry = self._cache.get(key)
        if entry is None or entry.is_expired:
            return None
        return entry.value

    async def set(self, context: dict[str, Any], value: Any, ttl: int = 300) -> None:
        key = self._make_key(context)
        self._cache[key] = CacheEntry(value, ttl)

    async def clear(self) -> None:
        self._cache.clear()
