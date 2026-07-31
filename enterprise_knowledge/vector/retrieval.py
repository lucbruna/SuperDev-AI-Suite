"""Retrieval over the vector database."""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.vector.similarity_search import SimilaritySearch
from enterprise_knowledge.vector.vector_database import VectorDatabase


class VectorRetrieval:
    """Searches the vector database for contextually related items."""

    def __init__(self, database: VectorDatabase | None = None,
                 similarity: SimilaritySearch | None = None) -> None:
        self.database = database or VectorDatabase()
        self.similarity = similarity or SimilaritySearch(metric="cosine")

    def search(self, query_vector: list[float],
               limit: int = 10,
               threshold: float = 0.0,
               filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        candidates = []
        for item in self.database.all():
            metadata = item["metadata"]
            if filters:
                matched = True
                for key, value in filters.items():
                    if metadata.get(key) != value:
                        matched = False
                        break
                if not matched:
                    continue
            candidates.append({"vector_id": item["vector_id"],
                               "vector": item["vector"],
                               "text": metadata.get("text", ""),
                               "metadata": metadata})
        results = self.similarity.rank(query_vector, candidates, limit)
        return [r for r in results if r["score"] >= threshold]

    def text_search(self, text: str, embeddings: Any,
                    limit: int = 10,
                    threshold: float = 0.0) -> list[dict[str, Any]]:
        vector = embeddings.embed(text)
        return self.search(vector, limit=limit, threshold=threshold)

    def stats(self) -> dict[str, Any]:
        return self.database.stats()
