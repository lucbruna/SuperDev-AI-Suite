from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from .knowledge_config import KnowledgeConfig, ResearchConfig, DocumentConfig, VectorMemoryConfig, EmbeddingConfig, ReasoningConfig, LearningConfig, ValidationConfig, KnowledgeGraphConfig
from .knowledge_models import (
    KnowledgeEntry, KnowledgeSource, KnowledgeType, KnowledgeState,
    ResearchQuery, DocumentAnalysis, EmbeddingVector,
    ReasoningResult, ValidationResult, Hypothesis,
)

logger = logging.getLogger(__name__)


class KnowledgeFactory:
    @staticmethod
    def create_knowledge_entry(title: str, content: str,
                                knowledge_type: KnowledgeType = KnowledgeType.EXPLICIT,
                                domain: str = "general",
                                source: Optional[KnowledgeSource] = None,
                                tags: Optional[List[str]] = None,
                                metadata: Optional[Dict[str, Any]] = None) -> KnowledgeEntry:
        return KnowledgeEntry(
            id=str(uuid.uuid4()),
            title=title,
            content=content,
            knowledge_type=knowledge_type,
            state=KnowledgeState.PENDING,
            source=source,
            tags=tags or [],
            domain=domain,
            metadata=metadata or {},
        )

    @staticmethod
    def create_research_query(query: str, domain: str = "general",
                               max_sources: int = 10,
                               depth: str = "standard",
                               user_id: Optional[str] = None) -> ResearchQuery:
        return ResearchQuery(
            id=str(uuid.uuid4()),
            query=query,
            domain=domain,
            max_sources=max_sources,
            depth=depth,
            user_id=user_id,
        )

    @staticmethod
    def create_document_analysis(document_id: str, title: str = "",
                                  content: str = "") -> DocumentAnalysis:
        return DocumentAnalysis(
            id=str(uuid.uuid4()),
            document_id=document_id,
            title=title,
            content=content,
        )

    @staticmethod
    def create_embedding(vector: List[float], model_name: str = "default",
                          metadata: Optional[Dict[str, Any]] = None) -> EmbeddingVector:
        return EmbeddingVector(
            id=str(uuid.uuid4()),
            vector=vector,
            dimension=len(vector),
            model_name=model_name,
            metadata=metadata or {},
        )

    @staticmethod
    def create_reasoning_result(query: str, conclusion: str = "",
                                 reasoning_type: str = "deductive",
                                 hypotheses: Optional[List[Hypothesis]] = None) -> ReasoningResult:
        return ReasoningResult(
            id=str(uuid.uuid4()),
            query=query,
            conclusion=conclusion,
            hypotheses=hypotheses or [],
            reasoning_type=reasoning_type,
        )

    @staticmethod
    def create_validation(entry_id: str, valid: bool = False,
                           confidence: float = 0.0,
                           validator: str = "system") -> ValidationResult:
        return ValidationResult(
            id=str(uuid.uuid4()),
            entry_id=entry_id,
            valid=valid,
            confidence=confidence,
            validator=validator,
        )

    @staticmethod
    def create_source(title: str, url: str = "",
                       source_type: str = "web",
                       author: str = "") -> KnowledgeSource:
        return KnowledgeSource(
            id=str(uuid.uuid4()),
            title=title,
            url=url,
            source_type=source_type,
            author=author,
        )

    @staticmethod
    def create_hypothesis(statement: str, confidence: float = 0.5) -> Hypothesis:
        return Hypothesis(
            id=str(uuid.uuid4()),
            statement=statement,
            confidence=confidence,
        )