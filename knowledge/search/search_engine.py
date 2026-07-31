from __future__ import annotations

import logging
from typing import Any

from ..indexing.index_manager import IndexManager
from ..knowledge_config import KnowledgeConfig
from ..knowledge_events import KnowledgeEvents, KnowledgeEventType
from ..knowledge_interfaces import EmbeddingProvider, VectorStore
from ..knowledge_metrics import KnowledgeMetrics
from ..knowledge_models import SearchResult
from ..vector_store.storage import InMemoryVectorStorage
from .keyword_search import KeywordSearch
from .query_parser import QueryParser
from .result_ranker import ResultRanker
from .semantic_search import SemanticSearch


class SearchEngine:
    """Composes keyword and semantic search into a fused ranking."""

    def __init__(
        self,
        vector_store: VectorStore | None = None,
        embedding_provider: EmbeddingProvider | None = None,
        index_manager: IndexManager | None = None,
        config: KnowledgeConfig | None = None,
        events: KnowledgeEvents | None = None,
        metrics: KnowledgeMetrics | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.search.engine")
        self.config = config or KnowledgeConfig()
        self.events = events or KnowledgeEvents()
        self.metrics = metrics or KnowledgeMetrics()
        self.index_manager = index_manager or IndexManager()
        self.vector_store = vector_store or InMemoryVectorStorage(self.config.similarity_threshold)
        self.keyword = KeywordSearch(self.index_manager)
        self.semantic = SemanticSearch(self.vector_store, embedding_provider)
        self.ranker = ResultRanker()
        self.parser = QueryParser()

    def search(self, query: str, top_k: int = 5, threshold: float = 0.0) -> list[SearchResult]:
        clean_query = self.parser.clean_query(query)
        keyword_hits = self.keyword.search(clean_query, top_k=top_k * 2)
        semantic_hits = self.semantic.search(clean_query, top_k=top_k * 2, threshold=threshold)
        fused = self.ranker.fuse(keyword_hits, semantic_hits)
        results = self.ranker.top_k(fused, top_k)
        self.metrics.increment("search.fused")
        self.events.emit(KnowledgeEventType.SEARCH_EXECUTED, {"hits": len(results)})
        return results
