from __future__ import annotations

from typing import Any

from .vector_database import VectorDatabase


class VectorRepository:
    """Repository layer for vector operations."""

    def __init__(self):
        self.db = VectorDatabase()

    def save_vector(self, id: str, vector: list[float], metadata: dict[str, Any] | None = None) -> None:
        self.db.insert(id, vector, metadata)

    def get_vector(self, id: str) -> list[float] | None:
        return self.db.get(id)

    def delete_vector(self, id: str) -> None:
        self.db.delete(id)

    def count(self) -> int:
        return self.db.count()
