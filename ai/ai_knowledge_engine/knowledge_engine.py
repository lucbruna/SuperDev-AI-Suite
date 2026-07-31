"""Knowledge Engine — Core knowledge management engine."""
from typing import Dict, Any, List, Optional
from datetime import datetime
from .knowledge_models import (
    Knowledge, Document, ResearchQuery, ResearchResult, LearningExperience,
    KnowledgeType, SourceType, ConfidenceLevel, ValidationStatus, LearningPhase,
    EmbeddingVector,
)
from .knowledge_config import KnowledgeConfig


class KnowledgeEngine:
    def __init__(self, config: Optional[KnowledgeConfig] = None):
        self._config = config or KnowledgeConfig()
        self._knowledge: Dict[str, Knowledge] = {}
        self._documents: Dict[str, Document] = {}
        self._experiences: Dict[str, LearningExperience] = {}
        self._embeddings: Dict[str, EmbeddingVector] = {}

    def store_knowledge(self, knowledge: Knowledge) -> Knowledge:
        self._knowledge[knowledge.knowledge_id] = knowledge
        return knowledge

    def get_knowledge(self, knowledge_id: str) -> Optional[Knowledge]:
        kb = self._knowledge.get(knowledge_id)
        if kb:
            kb.accessed_at = datetime.now()
            kb.access_count += 1
        return kb

    def search_knowledge(self, query: str, knowledge_type: Optional[KnowledgeType] = None) -> List[Knowledge]:
        results = list(self._knowledge.values())
        if knowledge_type:
            results = [k for k in results if k.knowledge_type == knowledge_type]
        query_lower = query.lower()
        results = [k for k in results if query_lower in k.title.lower() or query_lower in k.content.lower()]
        return sorted(results, key=lambda k: k.access_count, reverse=True)

    def update_knowledge(self, knowledge_id: str, content: Optional[str] = None, title: Optional[str] = None) -> bool:
        kb = self._knowledge.get(knowledge_id)
        if not kb:
            return False
        if content is not None:
            kb.content = content
        if title is not None:
            kb.title = title
        kb.updated_at = datetime.now()
        kb.version += 1
        return True

    def delete_knowledge(self, knowledge_id: str) -> bool:
        return self._knowledge.pop(knowledge_id, None) is not None

    def store_document(self, document: Document) -> Document:
        self._documents[document.document_id] = document
        return document

    def get_document(self, document_id: str) -> Optional[Document]:
        return self._documents.get(document_id)

    def record_experience(self, experience: LearningExperience) -> LearningExperience:
        self._experiences[experience.experience_id] = experience
        return experience

    def get_experience(self, experience_id: str) -> Optional[LearningExperience]:
        return self._experiences.get(experience_id)

    def store_embedding(self, embedding: EmbeddingVector) -> EmbeddingVector:
        self._embeddings[embedding.vector_id] = embedding
        return embedding

    def get_related_knowledge(self, knowledge_id: str) -> List[Knowledge]:
        kb = self._knowledge.get(knowledge_id)
        if not kb:
            return []
        return [self._knowledge[rid] for rid in kb.related_ids if rid in self._knowledge]

    def link_knowledge(self, knowledge_id: str, related_id: str) -> bool:
        kb = self._knowledge.get(knowledge_id)
        if not kb:
            return False
        if related_id not in kb.related_ids:
            kb.related_ids.append(related_id)
        return True

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_knowledge": len(self._knowledge),
            "total_documents": len(self._documents),
            "total_experiences": len(self._experiences),
            "total_embeddings": len(self._embeddings),
            "knowledge_by_type": len(set(k.knowledge_type.value for k in self._knowledge.values())),
            "validated": len([k for k in self._knowledge.values() if k.validation_status == ValidationStatus.VALIDATED]),
            "pending_validation": len([k for k in self._knowledge.values() if k.validation_status == ValidationStatus.PENDING]),
        }
