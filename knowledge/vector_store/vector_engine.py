from __future__ import annotations

import logging
from typing import Any

from ..embeddings.similarity import Similarity
from ..knowledge_config import KnowledgeConfig
from ..knowledge_events import KnowledgeEvents, KnowledgeEventType
from ..knowledge_interfaces import VectorStore
from ..knowledge_metrics import KnowledgeMetrics
from ..knowledge_models import Embedding, SearchResult
from .collection_manager import CollectionManager
from .filtering import Filtering
from .index_manager import IndexManager
from .ranking import Ranking
from .storage import InMemoryVectorStorage


class VectorEngine:
    """Composes the vector store, collections, and search strategies."""

    def __init__(
        self,
        store: VectorStore | None = None,
        config: KnowledgeConfig | None = None,
        events: KnowledgeEvents | None = None,
        metrics: KnowledgeMetrics | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.vector_store.engine")
        self.config = config or KnowledgeConfig()
        self.events = events or KnowledgeEvents()
        self.metrics = metrics or KnowledgeMetrics()
        self.store = store or InMemoryVectorStorage(self.config.similarity_threshold)
        self.collections = CollectionManager()
        self.index = IndexManager()
        self.filtering = Filtering()
        self.ranking = Ranking()

    def add(self, embedding: Embedding, collection: str | None = None) -> str:
        embedding_id = self.store.add(embedding)
        if collection:
            self.collections.add(collection, embedding)
        self.index.add(embedding)
        self.metrics.increment("vector_store.vectors")
        self.events.emit(KnowledgeEventType.INDEX_UPDATED, {"embedding_id": embedding_id})
        return embedding_id

    def search(self, query_vector: list[float], top_k: int = 5,
               collection: str | None = None, metadata_eq: dict[str, Any] | None = None) -> list[SearchResult]:
        if collection:
            results = self.collections.search(collection, query_vector, top_k, self.config.similarity_threshold, metadata_eq)
        else:
            results = self.store.search(query_vector, top_k)
            results = self.filtering.apply(results, metadata_eq=metadata_eq)
        return self.ranking.top_k(self.ranking.sort_by_score(results), top_k)

    def stats(self) -> dict[str, Any]:
        return {
            "vectors": self.store.count(),
            "collections": self.collections.list(),
            "indexed": self.index.count(),
        }

    def clear(self) -> None:
        self.store.clear()
