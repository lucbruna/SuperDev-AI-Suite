"""Vector engine: memória semântica do Enterprise Knowledge.

Permite perguntas como "Como resolvemos esse problema no sistema anterior?"
buscando por similaridade semântica em documentos, códigos e históricos.
"""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.knowledge_config import EnterpriseKnowledgeConfig
from enterprise_knowledge.knowledge_events import (EnterpriseKnowledgeEvents,
                                                   EnterpriseKnowledgeEventType)
from enterprise_knowledge.knowledge_logger import get_logger
from enterprise_knowledge.knowledge_metrics import EnterpriseKnowledgeMetrics
from enterprise_knowledge.knowledge_registry import EnterpriseKnowledgeRegistry
from enterprise_knowledge.knowledge_security import EnterpriseKnowledgeSecurity
from enterprise_knowledge.vector.embedding_manager import EmbeddingManager
from enterprise_knowledge.vector.indexing import VectorIndexing
from enterprise_knowledge.vector.retrieval import VectorRetrieval
from enterprise_knowledge.vector.similarity_search import SimilaritySearch
from enterprise_knowledge.vector.vector_database import VectorDatabase


class VectorEngine:
    """Orquestrador da memória vetorial (Fase 3 do Volume 27)."""

    def __init__(self, events: EnterpriseKnowledgeEvents | None = None,
                 metrics: EnterpriseKnowledgeMetrics | None = None,
                 config: EnterpriseKnowledgeConfig | None = None,
                 security: EnterpriseKnowledgeSecurity | None = None,
                 registry: EnterpriseKnowledgeRegistry | None = None,
                 database: VectorDatabase | None = None,
                 embeddings: EmbeddingManager | None = None) -> None:
        self._log = get_logger("vector")
        self.events = events or EnterpriseKnowledgeEvents()
        self.metrics = metrics or EnterpriseKnowledgeMetrics()
        self.config = config or EnterpriseKnowledgeConfig()
        self.security = security or EnterpriseKnowledgeSecurity()
        self.registry = registry
        self.database = database or VectorDatabase()
        self.embeddings = embeddings or EmbeddingManager(
            dimensions=self.config.get("embedding_dimensions", 32))
        self.indexer = VectorIndexing(embeddings=self.embeddings)
        self.retrieval = VectorRetrieval(database=self.database)

    def embed(self, text: str) -> list[float]:
        return self.embeddings.embed(text)

    def add_text(self, text: str, vector_id: str = "",
                 metadata: dict[str, Any] | None = None) -> str:
        if not vector_id:
            vector_id = f"vec-{abs(hash(text)) % 10**8:08d}"
        vector = self.embeddings.embed(text)
        payload = dict(metadata or {})
        payload["text"] = text
        self.database.upsert(vector_id, vector, payload)
        self.metrics.increment("ek.vectors")
        return vector_id

    def add_document(self, document_id: str, text: str,
                     tags: list[str] | None = None) -> list[str]:
        chunks = self.indexer.index_text(
            text, prefix=document_id,
            metadata={"document_id": document_id, "tags": tags or []})
        chunk_ids = []
        for chunk in chunks:
            vector_id = chunk["chunk_id"]
            self.database.upsert(vector_id, chunk["vector"],
                                 {"text": chunk["text"],
                                  "document_id": document_id,
                                  "tags": tags or []})
            chunk_ids.append(vector_id)
        self.metrics.increment("ek.vectors", len(chunk_ids))
        self.metrics.increment("ek.documents")
        self.events.publish(EnterpriseKnowledgeEventType.DOCUMENT_INDEXED,
                            {"document_id": document_id,
                             "chunks": len(chunk_ids)})
        return chunk_ids

    def query(self, text: str, limit: int = 10,
              threshold: float = 0.0,
              filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        vector = self.embeddings.embed(text)
        results = self.retrieval.search(vector, limit=limit,
                                        threshold=threshold,
                                        filters=filters)
        self.metrics.increment("ek.searches")
        self.events.publish(EnterpriseKnowledgeEventType.SEARCH_EXECUTED,
                            {"query": text, "hits": len(results)})
        return results

    def answer_question(self, question: str, limit: int = 3) -> dict[str, Any]:
        """'Por que o módulo financeiro foi alterado?' -> evidence snippets."""
        results = self.query(question, limit=limit)
        return {"question": question,
                "snippets": [{"text": r.get("text", ""),
                              "document_id": r.get("metadata", {}).get(
                                  "document_id", ""),
                              "score": r.get("score", 0.0)}
                             for r in results]}

    def delete(self, vector_id: str) -> bool:
        return self.database.delete(vector_id)

    def stats(self) -> dict[str, Any]:
        return {"database": self.database.stats(),
                "embeddings": self.embeddings.stats(),
                "searches": self.metrics.snapshot()["counters"].get(
                    "ek.searches", 0)}
