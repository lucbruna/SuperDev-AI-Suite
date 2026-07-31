from __future__ import annotations

from datetime import UTC, datetime, timedelta

from .reasoning_models import ReasoningResult


class ReasoningCache:
    """Cache for reasoning results to avoid redundant computation."""

    def __init__(self, ttl_seconds: int = 300):
        self._ttl = timedelta(seconds=ttl_seconds)
        self._cache: dict[str, tuple[ReasoningResult, datetime]] = {}

    def get(self, key: str) -> ReasoningResult | None:
        entry = self._cache.get(key)
        if entry is None:
            return None
        result, timestamp = entry
        if datetime.now(UTC) - timestamp > self._ttl:
            del self._cache[key]
            return None
        return result

    def set(self, key: str, result: ReasoningResult) -> None:
        self._cache[key] = (result, datetime.now(UTC))

    def invalidate(self, key: str) -> bool:
        return self._cache.pop(key, None) is not None

    def clear(self) -> None:
        self._cache.clear()

    def size(self) -> int:
        return len(self._cache)
