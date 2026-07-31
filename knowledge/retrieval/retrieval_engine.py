from __future__ import annotations

import logging
from typing import Any

from ..knowledge_config import KnowledgeConfig
from ..knowledge_events import KnowledgeEvents, KnowledgeEventType
from ..knowledge_interfaces import EmbeddingProvider, MemoryStore, VectorStore
from ..knowledge_metrics import KnowledgeMetrics
from ..knowledge_models import RetrievalContext, SearchResult
from ..vector_store.storage import InMemoryVectorStorage
from .context_assembler import ContextAssembler
from .fusion import Fusion
from .reranker import Reranker
from .retriever import Retriever


class RetrievalEngine:
    """Composes multi-source retrieval, fusion, reranking, and context assembly."""

    def __init__(
        self,
        vector_store: VectorStore | None = None,
        embedding_provider: EmbeddingProvider | None = None,
        memory_store: MemoryStore | None = None,
        graph_engine: Any | None = None,
        config: KnowledgeConfig | None = None,
        events: KnowledgeEvents | None = None,
        metrics: KnowledgeMetrics | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.retrieval.engine")
        self.config = config or KnowledgeConfig()
        self.events = events or KnowledgeEvents()
        self.metrics = metrics or KnowledgeMetrics()
        self.vector_store = vector_store or InMemoryVectorStorage(self.config.similarity_threshold)
        self.retriever = Retriever(self.vector_store, embedding_provider, memory_store, graph_engine)
        self.fusion = Fusion()
        self.reranker = Reranker()
        self.assembler = ContextAssembler()

    def retrieve(self, query: str, top_k: int = 5) -> RetrievalContext:
        candidates = self.retriever.retrieve(query, top_k=top_k * 2)
        fused = self.fusion.fuse([candidates])
        reranked = self.reranker.rerank(query, fused, top_k=top_k)
        context = self.assembler.assemble(query, reranked)
        self.metrics.increment("retrieval.executed")
        self.events.emit(KnowledgeEventType.SEARCH_EXECUTED, {"hits": len(reranked)})
        return context

    def retrieve_sources(self, query: str, top_k: int = 5) -> dict[str, list[SearchResult]]:
        return {
            "vector": self.retriever._from_vector(query, top_k),
            "memory": self.retriever._from_memory(query, top_k),
            "graph": self.retriever._from_graph(query, top_k),
        }
