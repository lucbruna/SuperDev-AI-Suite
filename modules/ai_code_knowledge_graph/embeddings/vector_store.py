"""Vector store — cosine-similarity retrieval over embedded items.

Pure-Python implementation (no numpy dependency): :class:`MemoryVectorStore`
keeps items in memory and ranks by cosine similarity; :class:`PersistentVectorStore`
adds JSON save/load so a build can be reused across processes.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

SearchResult = tuple[str, float, dict[str, Any]]


class VectorStore:
    """Base class for vector stores."""

    def add(self, item_id: str, vector: list[float], payload: dict[str, Any] | None = None) -> None:
        raise NotImplementedError

    def search(self, vector: list[float], k: int = 5) -> list[SearchResult]:
        raise NotImplementedError

    def size(self) -> int:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError

    def remove(self, item_id: str) -> None:
        raise NotImplementedError


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Cosine similarity between two equal-length vectors (0.0 on degenerate)."""
    if len(left) != len(right) or not left:
        return 0.0
    dot = 0.0
    norm_left = 0.0
    norm_right = 0.0
    for a, b in zip(left, right):
        dot += a * b
        norm_left += a * a
        norm_right += b * b
    if norm_left == 0.0 or norm_right == 0.0:
        return 0.0
    return dot / (math.sqrt(norm_left) * math.sqrt(norm_right))


class MemoryVectorStore(VectorStore):
    """In-memory vector store with pure-Python cosine ranking."""

    def __init__(self) -> None:
        self._items: dict[str, tuple[list[float], dict[str, Any]]] = {}

    def add(self, item_id: str, vector: list[float], payload: dict[str, Any] | None = None) -> None:
        self._items[item_id] = (list(vector), dict(payload or {}))

    def search(self, vector: list[float], k: int = 5) -> list[SearchResult]:
        scored = [(item_id, cosine_similarity(vector, stored), payload) for item_id, (stored, payload) in self._items.items()]
        scored.sort(key=lambda entry: entry[1], reverse=True)
        return [(item_id, score, payload) for item_id, score, payload in scored[: max(0, k)]]

    def size(self) -> int:
        return len(self._items)

    def clear(self) -> None:
        self._items.clear()

    def remove(self, item_id: str) -> None:
        self._items.pop(item_id, None)

    def get(self, item_id: str) -> tuple[list[float], dict[str, Any]] | None:
        return self._items.get(item_id)

    def to_json(self) -> dict[str, Any]:
        return {item_id: {"vector": vector, "payload": payload} for item_id, (vector, payload) in self._items.items()}

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "MemoryVectorStore":
        store = cls()
        for item_id, entry in data.items():
            store.add(item_id, entry.get("vector", []), entry.get("payload", {}))
        return store


class PersistentVectorStore(MemoryVectorStore):
    """Memory store that can be saved to and loaded from a JSON file."""

    def __init__(self, path: str | Path | None = None) -> None:
        super().__init__()
        self.path = Path(path) if path else None
        if self.path and self.path.exists():
            self._items = MemoryVectorStore.from_json(json.loads(self.path.read_text(encoding="utf-8")))._items

    def save(self) -> None:
        if self.path is None:
            raise ValueError("PersistentVectorStore has no path configured")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.to_json(), ensure_ascii=False), encoding="utf-8")
