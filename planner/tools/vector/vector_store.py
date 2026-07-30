from __future__ import annotations

from typing import Any

from .vector_database import VectorDatabase


class VectorStore:
    """High-level vector store with search capabilities."""

    def __init__(self):
        self.db = VectorDatabase()

    def add(self, id: str, vector: list[float], metadata: dict[str, Any] | None = None) -> None:
        self.db.insert(id, vector, metadata)

    def remove(self, id: str) -> None:
        self.db.delete(id)

    def search(self, query_vector: list[float], top_k: int = 10) -> list[dict[str, Any]]:
        return []

    def health(self) -> dict[str, Any]:
        return {"status": "healthy", "vectors": self.db.count()}
