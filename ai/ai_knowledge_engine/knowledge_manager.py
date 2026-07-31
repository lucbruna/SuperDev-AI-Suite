"""Knowledge Manager — High-level knowledge management operations."""

from typing import Any

from .knowledge_engine import KnowledgeEngine
from .knowledge_models import (
    ConfidenceLevel,
    Knowledge,
    KnowledgeType,
    SourceType,
    ValidationStatus,
)


class KnowledgeManager:
    def __init__(self, engine: KnowledgeEngine | None = None):
        self._engine = engine or KnowledgeEngine()

    @property
    def engine(self) -> KnowledgeEngine:
        return self._engine

    def add_knowledge(
        self,
        title: str,
        content: str,
        knowledge_type: str = "fact",
        source: str = "user_input",
        tags: list[str] | None = None,
    ) -> Knowledge:
        kt = KnowledgeType(knowledge_type) if knowledge_type in [e.value for e in KnowledgeType] else KnowledgeType.FACT
        st = SourceType(source) if source in [e.value for e in SourceType] else SourceType.USER_INPUT
        kb = Knowledge(title=title, content=content, knowledge_type=kt, source=st, tags=tags or [])
        return self._engine.store_knowledge(kb)

    def find_knowledge(self, query: str, knowledge_type: str | None = None) -> list[Knowledge]:
        kt = KnowledgeType(knowledge_type) if knowledge_type else None
        return self._engine.search_knowledge(query, kt)

    def get_knowledge(self, knowledge_id: str) -> Knowledge | None:
        return self._engine.get_knowledge(knowledge_id)

    def update_knowledge(self, knowledge_id: str, content: str | None = None, title: str | None = None) -> bool:
        return self._engine.update_knowledge(knowledge_id, content, title)

    def delete_knowledge(self, knowledge_id: str) -> bool:
        return self._engine.delete_knowledge(knowledge_id)

    def link_concepts(self, knowledge_id: str, related_id: str) -> bool:
        return self._engine.link_knowledge(knowledge_id, related_id)

    def validate_knowledge(self, knowledge_id: str, confidence: ConfidenceLevel = ConfidenceLevel.HIGH) -> bool:
        kb = self._engine.get_knowledge(knowledge_id)
        if not kb:
            return False
        kb.confidence = confidence
        kb.validation_status = ValidationStatus.VALIDATED
        return True

    def get_unvalidated(self) -> list[Knowledge]:
        all_knowledge = list(self._engine._knowledge.values())
        return [k for k in all_knowledge if k.validation_status == ValidationStatus.PENDING]

    def get_by_type(self, knowledge_type: str) -> list[Knowledge]:
        kt = KnowledgeType(knowledge_type) if knowledge_type in [e.value for e in KnowledgeType] else None
        return [k for k in self._engine._knowledge.values() if k.knowledge_type == kt]

    def get_top_knowledge(self, limit: int = 10) -> list[Knowledge]:
        all_knowledge = list(self._engine._knowledge.values())
        return sorted(all_knowledge, key=lambda k: k.access_count, reverse=True)[:limit]

    def get_stats(self) -> dict[str, Any]:
        return self._engine.get_stats()
