"""In-memory vector database."""

from __future__ import annotations

import threading
import uuid
from typing import Any


class VectorDatabase:
    """Thread-safe in-memory vector store keyed by vector_id."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._vectors: dict[str, list[float]] = {}
        self._metadata: dict[str, dict[str, Any]] = {}

    def upsert(self, vector_id: str, vector: list[float],
               metadata: dict[str, Any] | None = None) -> None:
        with self._lock:
            self._vectors[vector_id] = list(vector)
            self._metadata[vector_id] = dict(metadata or {})

    def get(self, vector_id: str) -> list[float] | None:
        with self._lock:
            vector = self._vectors.get(vector_id)
            return list(vector) if vector is not None else None

    def metadata_for(self, vector_id: str) -> dict[str, Any]:
        with self._lock:
            return dict(self._metadata.get(vector_id, {}))

    def all(self) -> list[dict[str, Any]]:
        with self._lock:
            return [{"vector_id": vid, "vector": list(v),
                     "metadata": dict(self._metadata.get(vid, {}))}
                    for vid, v in self._vectors.items()]

    def delete(self, vector_id: str) -> bool:
        with self._lock:
            removed = self._vectors.pop(vector_id, None) is not None
            self._metadata.pop(vector_id, None)
            return removed

    def clear(self) -> None:
        with self._lock:
            self._vectors.clear()
            self._metadata.clear()

    def count(self) -> int:
        with self._lock:
            return len(self._vectors)

    def stats(self) -> dict[str, Any]:
        with self._lock:
            dims = len(next(iter(self._vectors.values()))) \
                if self._vectors else 0
        return {"vectors": self.count(), "dimensions": dims}

    def _new_id(self) -> str:
        return f"vec-{uuid.uuid4().hex[:8]}"
