"""Extraction engine: coordinates parsing, entities, relations and classes."""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.extraction.classifier import TextClassifier
from enterprise_knowledge.extraction.entity_extractor import EntityExtractor
from enterprise_knowledge.extraction.information_parser import InformationParser
from enterprise_knowledge.extraction.relation_extractor import RelationExtractor
from enterprise_knowledge.knowledge_config import EnterpriseKnowledgeConfig
from enterprise_knowledge.knowledge_events import (EnterpriseKnowledgeEvents,
                                                   EnterpriseKnowledgeEventType)
from enterprise_knowledge.knowledge_logger import get_logger
from enterprise_knowledge.knowledge_metrics import EnterpriseKnowledgeMetrics
from enterprise_knowledge.knowledge_models import ExtractionResult
from enterprise_knowledge.knowledge_security import EnterpriseKnowledgeSecurity


class ExtractionEngine:
    """Orquestrador de extração (Fase 7 do Volume 27)."""

    def __init__(self, events: EnterpriseKnowledgeEvents | None = None,
                 metrics: EnterpriseKnowledgeMetrics | None = None,
                 config: EnterpriseKnowledgeConfig | None = None,
                 security: EnterpriseKnowledgeSecurity | None = None) -> None:
        self._log = get_logger("extraction")
        self.events = events or EnterpriseKnowledgeEvents()
        self.metrics = metrics or EnterpriseKnowledgeMetrics()
        self.config = config or EnterpriseKnowledgeConfig()
        self.security = security or EnterpriseKnowledgeSecurity()
        self.entities = EntityExtractor()
        self.relations = RelationExtractor()
        self.information = InformationParser()
        self.classifier = TextClassifier()

    def extract(self, text: str) -> ExtractionResult:
        entity_list = self.entities.extract_with_types(text)
        relation_list = self.relations.extract(text)
        summary = self.summarize(text)
        result = ExtractionResult(entities=entity_list,
                                  relations=relation_list,
                                  summary=summary)
        self.metrics.increment("ek.extractions")
        self.events.publish(EnterpriseKnowledgeEventType.EXTRACTION_COMPLETED,
                            {"entities": len(entity_list),
                             "relations": len(relation_list)})
        return result

    def extract_entities(self, text: str) -> list[dict[str, Any]]:
        return self.entities.extract_with_types(text)

    def extract_relations(self, text: str) -> list[dict[str, Any]]:
        return self.relations.extract(text)

    def parse_information(self, text: str) -> dict[str, Any]:
        return self.information.parse(text)

    def classify(self, text: str) -> dict[str, Any]:
        return self.classifier.classify(text)

    def summarize(self, text: str, limit: int = 2) -> str:
        sentences = [s.strip() for s in
                     (text or "").replace("\n", " ").split(".") if s.strip()]
        if not sentences:
            return ""
        return ". ".join(sentences[:limit]) + "."

    def stats(self) -> dict[str, Any]:
        return self.metrics.snapshot()["counters"]
