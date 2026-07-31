"""Semantic memory: general facts and concepts."""

from __future__ import annotations

import time
from typing import Any

from enterprise_knowledge.knowledge_models import MemoryRecord, MemoryType
from enterprise_knowledge.knowledge_protocols import new_id, tokenize
from enterprise_knowledge.vector.vector_engine import VectorEngine


class SemanticMemory:
    """Stores facts; optionally indexes them into the vector store."""

    def __init__(self, vectors: VectorEngine | None = None) -> None:
        self.vectors = vectors
        self._facts: dict[str, MemoryRecord] = {}

    def remember_fact(self, fact: str, subject: str = "",
                      metadata: dict[str, Any] | None = None) -> MemoryRecord:
        record = MemoryRecord(memory_id=new_id("memory"),
                              memory_type=MemoryType.SEMANTIC,
                              content=fact, owner_id=subject,
                              metadata=dict(metadata or {}),
                              created_at=time.time())
        self._facts[record.memory_id] = record
        if self.vectors is not None:
            self.vectors.add_text(fact, vector_id=record.memory_id,
                                  metadata={"memory_id": record.memory_id,
                                            "text": fact})
        return record

    def recall(self, term: str) -> list[MemoryRecord]:
        term = term.lower()
        return [rec for rec in self._facts.values()
                if term in rec.content.lower()]

    def recall_similar(self, question: str, limit: int = 5) -> list[dict[str, Any]]:
        if self.vectors is None:
            return []
        return self.vectors.query(question, limit=limit)

    def facts_for(self, subject: str) -> list[MemoryRecord]:
        return [rec for rec in self._facts.values()
                if rec.owner_id == subject]

    def count(self) -> int:
        return len(self._facts)

    def clear(self) -> None:
        self._facts.clear()
