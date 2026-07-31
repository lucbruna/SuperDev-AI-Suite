"""Memory engine: unifies short/long-term, episodic, semantic and user memory."""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.knowledge_config import EnterpriseKnowledgeConfig
from enterprise_knowledge.knowledge_events import (EnterpriseKnowledgeEvents,
                                                   EnterpriseKnowledgeEventType)
from enterprise_knowledge.knowledge_logger import get_logger
from enterprise_knowledge.knowledge_metrics import EnterpriseKnowledgeMetrics
from enterprise_knowledge.knowledge_models import (AccessLevel, MemoryRecord,
                                                   MemoryType)
from enterprise_knowledge.knowledge_protocols import tokenize
from enterprise_knowledge.knowledge_registry import EnterpriseKnowledgeRegistry
from enterprise_knowledge.knowledge_security import EnterpriseKnowledgeSecurity
from enterprise_knowledge.memory.episodic_memory import EpisodicMemory
from enterprise_knowledge.memory.long_term import LongTermMemory
from enterprise_knowledge.memory.semantic_memory import SemanticMemory
from enterprise_knowledge.memory.short_term import ShortTermMemory
from enterprise_knowledge.memory.user_memory import UserMemory
from enterprise_knowledge.vector.vector_engine import VectorEngine


class MemoryEngine:
    """Orquestrador de memória (Fase 6 do Volume 27)."""

    def __init__(self, events: EnterpriseKnowledgeEvents | None = None,
                 metrics: EnterpriseKnowledgeMetrics | None = None,
                 config: EnterpriseKnowledgeConfig | None = None,
                 security: EnterpriseKnowledgeSecurity | None = None,
                 registry: EnterpriseKnowledgeRegistry | None = None,
                 vectors: VectorEngine | None = None) -> None:
        self._log = get_logger("memory")
        self.events = events or EnterpriseKnowledgeEvents()
        self.metrics = metrics or EnterpriseKnowledgeMetrics()
        self.config = config or EnterpriseKnowledgeConfig()
        self.security = security or EnterpriseKnowledgeSecurity()
        self.registry = registry
        self.vectors = vectors
        self.short_term = ShortTermMemory(
            capacity=self.config.get("short_term_capacity", 20))
        self.long_term = LongTermMemory()
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory(vectors=vectors)
        self.user = UserMemory()

    def remember(self, content: str, memory_type: MemoryType = MemoryType.LONG_TERM,
                 owner_id: str = "", importance: float = 0.5,
                 metadata: dict[str, Any] | None = None) -> MemoryRecord:
        if memory_type == MemoryType.SHORT_TERM:
            record = self.short_term.remember(content, owner_id, metadata)
        elif memory_type == MemoryType.EPISODIC:
            record = self.episodic.remember_event(content, owner_id, "", metadata)
        elif memory_type == MemoryType.SEMANTIC:
            record = self.semantic.remember_fact(content, owner_id, metadata)
        else:
            record = self.long_term.remember(content, owner_id, importance,
                                             metadata)
        if self.registry is not None:
            self.registry.register_memory(record)
        self.metrics.increment("ek.memories")
        self.events.publish(EnterpriseKnowledgeEventType.MEMORY_STORED,
                            {"memory_id": record.memory_id,
                             "memory_type": memory_type.value,
                             "owner_id": owner_id})
        return record

    def recall(self, term: str, limit: int = 5) -> list[MemoryRecord]:
        terms = [t for t in tokenize(term) if len(t) >= 3]
        results = (self.short_term.recall_containing(term)
                   + self.long_term.recall_containing(term)
                   + self.semantic.recall(term))
        if not results and terms:
            # Token-overlap fallback: finds memories sharing words with the
            # query even when the full phrase is not a substring.
            def overlaps(record: MemoryRecord) -> bool:
                content = record.content.lower()
                return any(t in content for t in terms)
            candidates: list[MemoryRecord] = []
            for term in terms:
                candidates.extend(self.short_term.recall_containing(term))
                candidates.extend(self.long_term.recall_containing(term))
                candidates.extend(self.semantic.recall(term))
            results = [rec for rec in candidates if overlaps(rec)]
        unique: dict[str, MemoryRecord] = {}
        for record in results:
            unique[record.memory_id] = record
        ordered = sorted(unique.values(),
                         key=lambda rec: rec.created_at, reverse=True)
        self.metrics.increment("ek.memory_recalls")
        self.events.publish(EnterpriseKnowledgeEventType.MEMORY_RECALLED,
                            {"term": term, "hits": len(ordered[:limit])})
        return ordered[:max(0, limit)]

    def recall_similar(self, question: str, limit: int = 5) -> list[dict[str, Any]]:
        self.events.publish(EnterpriseKnowledgeEventType.MEMORY_RECALLED,
                            {"term": question, "hits": 0})
        return self.semantic.recall_similar(question, limit=limit)

    def remember_event(self, action: str, actor: str = "",
                       context: str = "",
                       metadata: dict[str, Any] | None = None) -> MemoryRecord:
        record = self.episodic.remember_event(action, actor, context, metadata)
        if self.registry is not None:
            self.registry.register_memory(record)
        self.metrics.increment("ek.memories")
        self.events.publish(EnterpriseKnowledgeEventType.MEMORY_STORED,
                            {"memory_id": record.memory_id,
                             "memory_type": MemoryType.EPISODIC.value,
                             "owner_id": actor})
        return record

    def forget_short_term(self) -> None:
        self.short_term.clear()

    def stats(self) -> dict[str, Any]:
        return {
            "short_term": self.short_term.count(),
            "long_term": self.long_term.count(),
            "episodic": self.episodic.count(),
            "semantic": self.semantic.count(),
            "user_entries": self.user.count(),
            "counters": self.metrics.snapshot()["counters"],
        }
