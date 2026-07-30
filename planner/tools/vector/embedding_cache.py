from __future__ import annotations

from typing import Any


class EmbeddingCache:
    """Cache for embedding vectors."""

    def __init__(self, max_size: int = 10000):
        self._cache: dict[str, list[float]] = {}
        self._max_size = max_size

    def get(self, text: str) -> list[float] | None:
        return self._cache.get(text)

    def set(self, text: str, vector: list[float]) -> None:
        if len(self._cache) >= self._max_size:
            self._cache.pop(next(iter(self._cache)))
        self._cache[text] = vector

    def clear(self) -> None:
        self._cache.clear()

    def size(self) -> int:
        return len(self._cache)
