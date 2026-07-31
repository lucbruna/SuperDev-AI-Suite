from __future__ import annotations

from typing import Any


class TemplateCache:
    """Cache for compiled/parsed templates."""

    def __init__(self, max_size: int = 256) -> None:
        self._max_size = max_size
        self._cache: dict[str, Any] = {}

    def get(self, key: str) -> Any:
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        if len(self._cache) >= self._max_size:
            self._cache.pop(next(iter(self._cache)))
        self._cache[key] = value

    def clear(self) -> None:
        self._cache.clear()

    def remove(self, key: str) -> None:
        self._cache.pop(key, None)

    @property
    def size(self) -> int:
        return len(self._cache)
