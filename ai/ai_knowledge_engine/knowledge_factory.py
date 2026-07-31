"""Knowledge Factory — Factory for creating knowledge components."""
from typing import Dict, Any, List, Optional
from .knowledge_models import (
    Knowledge, Document, ResearchQuery, ResearchResult, LearningExperience,
    KnowledgeType, SourceType, ConfidenceLevel, ValidationStatus, LearningPhase,
    EmbeddingVector,
)


class KnowledgeFactory:
    @staticmethod
    def create_knowledge(title: str = "", content: str = "", knowledge_type: str = "fact", source: str = "user_input", tags: Optional[List[str]] = None) -> Knowledge:
        kt = KnowledgeType(knowledge_type) if knowledge_type in [e.value for e in KnowledgeType] else KnowledgeType.FACT
        st = SourceType(source) if source in [e.value for e in SourceType] else SourceType.USER_INPUT
        return Knowledge(title=title, content=content, knowledge_type=kt, source=st, tags=tags or [])

    @staticmethod
    def create_document(title: str = "", content: str = "", document_type: str = "text", source_path: str = "") -> Document:
        return Document(title=title, content=content, document_type=document_type, source_path=source_path)

    @staticmethod
    def create_research_query(query_text: str = "", query_type: str = "info", max_results: int = 10) -> ResearchQuery:
        return ResearchQuery(query_text=query_text, query_type=query_type, max_results=max_results)

    @staticmethod
    def create_research_result(title: str = "", content: str = "", source: str = "web", source_url: str = "", relevance_score: float = 0.0) -> ResearchResult:
        st = SourceType(source) if source in [e.value for e in SourceType] else SourceType.WEB
        return ResearchResult(title=title, content=content, source=st, source_url=source_url, relevance_score=relevance_score)

    @staticmethod
    def create_experience(title: str = "", description: str = "", outcome: str = "", success: bool = True, lessons: Optional[List[str]] = None) -> LearningExperience:
        return LearningExperience(title=title, description=description, outcome=outcome, success=success, lessons=lessons or [])

    @staticmethod
    def create_embedding(text: str = "", vector: Optional[List[float]] = None, model: str = "default") -> EmbeddingVector:
        return EmbeddingVector(text=text, vector=vector or [], model=model, dimensions=len(vector) if vector else 0)

    @staticmethod
    def templates() -> Dict[str, Dict[str, Any]]:
        return {
            "technical": {"type": "fact", "source": "document", "confidence": "high"},
            "business": {"type": "insight", "source": "user_input", "confidence": "medium"},
            "research": {"type": "concept", "source": "web", "confidence": "medium"},
            "experience": {"type": "experience", "source": "agent_experience", "confidence": "high"},
        }
