from __future__ import annotations

from typing import Any, Dict, List, Optional


class EmbeddingEntry:
    """A stored embedding entry."""

    def __init__(self, vector_id: str, vector: List[float], metadata: Dict[str, Any]):
        self._vector_id = vector_id
        self._vector = list(vector)
        self._metadata = dict(metadata)

    @property
    def vector_id(self) -> str:
        return self._vector_id

    @property
    def vector(self) -> List[float]:
        return list(self._vector)

    @property
    def metadata(self) -> Dict[str, Any]:
        return dict(self._metadata)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vector_id": self._vector_id,
            "vector": list(self._vector),
            "metadata": dict(self._metadata),
        }


class EmbeddingRepository:
    """Persistent repository for embedding storage and retrieval."""

    def __init__(self):
        self._entries: Dict[str, EmbeddingEntry] = {}

    @property
    def count(self) -> int:
        return len(self._entries)

    def store(self, vector_id: str, vector: List[float], metadata: Dict[str, Any]) -> EmbeddingEntry:
        entry = EmbeddingEntry(vector_id, vector, metadata)
        self._entries[vector_id] = entry
        return entry

    def get(self, vector_id: str) -> Optional[EmbeddingEntry]:
        return self._entries.get(vector_id)

    def update(self, vector_id: str, vector: List[float], metadata: Dict[str, Any]) -> bool:
        if vector_id not in self._entries:
            return False
        self._entries[vector_id] = EmbeddingEntry(vector_id, vector, metadata)
        return True

    def remove(self, vector_id: str) -> bool:
        return self._entries.pop(vector_id, None) is not None

    def list_ids(self) -> List[str]:
        return list(self._entries.keys())

    def list_entries(self) -> List[EmbeddingEntry]:
        return list(self._entries.values())

    def clear(self) -> None:
        self._entries.clear()

    def search_by_metadata(self, key: str, value: Any) -> List[EmbeddingEntry]:
        return [e for e in self._entries.values() if e.metadata.get(key) == value]
