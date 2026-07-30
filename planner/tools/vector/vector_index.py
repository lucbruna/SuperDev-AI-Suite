from __future__ import annotations

from typing import Any


class VectorIndex:
    """Index structure for efficient vector search."""

    def __init__(self):
        self._index: dict[str, list[float]] = {}

    def build(self, vectors: dict[str, list[float]]) -> None:
        self._index = dict(vectors)

    def add(self, id: str, vector: list[float]) -> None:
        self._index[id] = vector

    def remove(self, id: str) -> None:
        self._index.pop(id, None)

    def size(self) -> int:
        return len(self._index)

    def get_all(self) -> dict[str, list[float]]:
        return dict(self._index)
