from __future__ import annotations

import logging
from typing import Any

from ..knowledge_interfaces import EmbeddingProvider, MemoryStore, VectorStore
from ..knowledge_models import MemoryRecord, SearchResult
from ..vector_store.storage import InMemoryVectorStorage


class Retriever:
    """Retrieves candidate results from vector, keyword, memory, and graph sources."""

    def __init__(
        self,
        vector_store: VectorStore | None = None,
        embedding_provider: EmbeddingProvider | None = None,
        memory_store: MemoryStore | None = None,
        graph_engine: Any | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.retrieval.retriever")
        self.vector_store = vector_store or InMemoryVectorStorage()
        self.embedding_provider = embedding_provider
        self.memory_store = memory_store
        self.graph_engine = graph_engine

    def retrieve(self, query: str, top_k: int = 5) -> list[SearchResult]:
        sources = [
            self._from_vector(query, top_k),
            self._from_memory(query, top_k),
            self._from_graph(query, top_k),
        ]
        merged: list[SearchResult] = []
        for results in sources:
            merged.extend(results)
        merged.sort(key=lambda result: result.score, reverse=True)
        return merged[:top_k]

    def _from_vector(self, query: str, top_k: int) -> list[SearchResult]:
        if self.embedding_provider is None:
            return []
        vector = self.embedding_provider.embed(query)
        return self.vector_store.search(vector, top_k)

    def _from_memory(self, query: str, top_k: int) -> list[SearchResult]:
        if self.memory_store is None:
            return []
        records: list[MemoryRecord] = self.memory_store.list()
        query_tokens = set(query.lower().split())
        scored = []
        for record in records:
            overlap = len(query_tokens & set(record.content.lower().split()))
            score = record.importance + overlap * 0.1
            scored.append((score, record))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [
            SearchResult(text=record.content, score=score, source="memory",
                         metadata={"memory_type": record.memory_type})
            for score, record in scored[:top_k]
        ]

    def _from_graph(self, query: str, top_k: int) -> list[SearchResult]:
        if self.graph_engine is None:
            return []
        graph = self.graph_engine.graph if hasattr(self.graph_engine, "graph") else self.graph_engine
        related = []
        for entity in graph.entities():
            if entity.name.lower() in query.lower():
                related.extend(graph.neighbors(entity.name))
        return [
            SearchResult(text=neighbor, score=0.9, source="graph", metadata={"entity": True})
            for neighbor in related[:top_k]
        ]
