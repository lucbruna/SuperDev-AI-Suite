from __future__ import annotations

from typing import Any

from .vector_store import VectorStore


class VectorSync:
    """Synchronize vectors between stores or indexes."""

    def __init__(self, primary: VectorStore | None = None, secondary: VectorStore | None = None):
        self.primary = primary or VectorStore()
        self.secondary = secondary or VectorStore()

    def sync_add(self, doc_id: str, vector: list[float], metadata: dict[str, Any] | None = None) -> None:
        self.primary.add(doc_id, vector, metadata)
        self.secondary.add(doc_id, vector, metadata)

    def sync_remove(self, doc_id: str) -> None:
        self.primary.remove(doc_id)
        self.secondary.remove(doc_id)

    def sync_update(self, doc_id: str, vector: list[float], metadata: dict[str, Any] | None = None) -> None:
        self.sync_remove(doc_id)
        self.sync_add(doc_id, vector, metadata)

    def diff(self) -> list[dict[str, Any]]:
        """Return IDs present in one store but not the other."""
        # Simplified — real impl would need a way to list all IDs
        return []
