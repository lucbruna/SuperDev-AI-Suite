from __future__ import annotations

import logging
from typing import Any

from ..knowledge_interfaces import EmbeddingProvider, VectorStore
from ..knowledge_models import SearchResult
from ..vector_store.storage import InMemoryVectorStorage


class SemanticSearch:
    """Search over the vector store using query embeddings."""

    def __init__(
        self,
        vector_store: VectorStore | None = None,
        embedding_provider: EmbeddingProvider | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.search.semantic_search")
        self.vector_store = vector_store or InMemoryVectorStorage()
        self.embedding_provider = embedding_provider

    def search(self, query: str, top_k: int = 5, threshold: float = 0.0) -> list[SearchResult]:
        if self.embedding_provider is None:
            return []
        query_vector = self.embedding_provider.embed(query)
        results = self.vector_store.search(query_vector, top_k)
        return [result for result in results if result.score >= threshold]
