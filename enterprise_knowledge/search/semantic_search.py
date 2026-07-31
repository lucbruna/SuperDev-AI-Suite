"""Semantic search delegation to the vector subsystem."""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.vector.vector_engine import VectorEngine


class SemanticSearch:
    """Wraps the vector engine for semantic queries."""

    def __init__(self, vectors: VectorEngine | None = None) -> None:
        self.vectors = vectors

    def search(self, query: str, limit: int = 10,
               threshold: float = 0.0) -> list[dict[str, Any]]:
        if self.vectors is None:
            return []
        results = self.vectors.query(query, limit=limit,
                                     threshold=threshold)
        return [{"text": r.get("text", ""),
                 "score": r.get("score", 0.0),
                 "document_id": r.get("metadata", {}).get(
                     "document_id", ""),
                 "metadata": r.get("metadata", {})}
                for r in results]
