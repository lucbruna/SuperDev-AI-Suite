from __future__ import annotations

from typing import Any


class VectorDatabase:
    """Vector database for storing and searching embeddings."""

    def __init__(self):
        self._vectors: dict[str, list[float]] = {}
        self._metadata: dict[str, dict[str, Any]] = {}

    def insert(self, id: str, vector: list[float], metadata: dict[str, Any] | None = None) -> None:
        self._vectors[id] = vector
        self._metadata[id] = metadata or {}

    def delete(self, id: str) -> None:
        self._vectors.pop(id, None)
        self._metadata.pop(id, None)

    def get(self, id: str) -> list[float] | None:
        return self._vectors.get(id)

    def get_metadata(self, id: str) -> dict[str, Any] | None:
        return self._metadata.get(id)

    def count(self) -> int:
        return len(self._vectors)

    def clear(self) -> None:
        self._vectors.clear()
        self._metadata.clear()
