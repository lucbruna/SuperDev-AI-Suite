"""Document engine: ingests files and turns them into knowledge.

Feeds extracted content into the vector subsystem so documents can be
retrieved by semantic questions.
"""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.documents.classification import DocumentClassifier
from enterprise_knowledge.documents.document_manager import DocumentManager
from enterprise_knowledge.documents.extractor import EntityExtractor
from enterprise_knowledge.documents.metadata import MetadataExtractor
from enterprise_knowledge.documents.parser import DocumentParser
from enterprise_knowledge.knowledge_config import EnterpriseKnowledgeConfig
from enterprise_knowledge.knowledge_events import (EnterpriseKnowledgeEvents,
                                                   EnterpriseKnowledgeEventType)
from enterprise_knowledge.knowledge_logger import get_logger
from enterprise_knowledge.knowledge_metrics import EnterpriseKnowledgeMetrics
from enterprise_knowledge.knowledge_models import DocumentStatus
from enterprise_knowledge.knowledge_registry import EnterpriseKnowledgeRegistry
from enterprise_knowledge.knowledge_security import EnterpriseKnowledgeSecurity
from enterprise_knowledge.vector.vector_engine import VectorEngine


class DocumentEngine:
    """Orquestrador de documentos (Fase 4 do Volume 27)."""

    def __init__(self, events: EnterpriseKnowledgeEvents | None = None,
                 metrics: EnterpriseKnowledgeMetrics | None = None,
                 config: EnterpriseKnowledgeConfig | None = None,
                 security: EnterpriseKnowledgeSecurity | None = None,
                 registry: EnterpriseKnowledgeRegistry | None = None,
                 vectors: VectorEngine | None = None) -> None:
        self._log = get_logger("documents")
        self.events = events or EnterpriseKnowledgeEvents()
        self.metrics = metrics or EnterpriseKnowledgeMetrics()
        self.config = config or EnterpriseKnowledgeConfig()
        self.security = security or EnterpriseKnowledgeSecurity()
        self.registry = registry
        self.vectors = vectors
        self.parser = DocumentParser()
        self.metadata_extractor = MetadataExtractor()
        self.classifier = DocumentClassifier()
        self.extractor = EntityExtractor()
        self.manager = DocumentManager(registry=registry)

    def ingest(self, filename: str, content: str, source: str = "",
               tags: list[str] | None = None,
               index: bool = True) -> dict[str, Any]:
        parsed = self.parser.parse(filename, content)
        meta = self.metadata_extractor.extract(parsed["content"],
                                               title=parsed["title"],
                                               source=source)
        classification = self.classifier.classify(parsed["content"],
                                                  parsed["title"])
        entities = self.extractor.extract(parsed["content"])
        document = self.manager.register(
            title=parsed["title"], content=parsed["content"],
            source=source or meta.get("source", ""),
            file_type=parsed["file_type"],
            tags=list(tags or meta.get("tags", [])))
        document_id = document.document_id if document else ""
        summary = self.classifier.summarize(parsed["content"])
        result = {
            "document_id": document_id,
            "title": parsed["title"],
            "file_type": parsed["file_type"],
            "size": parsed["size"],
            "metadata": meta,
            "classification": classification,
            "summary": summary,
            "entities": entities["entities"],
            "relations": entities["relations"],
        }
        if index and self.vectors is not None and document_id:
            self.vectors.add_document(document_id, parsed["content"],
                                      tags=result["classification"].get(
                                          "category", "").split())
            if self.manager:
                self.manager.set_status(document_id,
                                        DocumentStatus.INDEXED)
        self.metrics.increment("ek.documents")
        self.events.publish(EnterpriseKnowledgeEventType.DOCUMENT_INDEXED,
                            {"document_id": document_id,
                             "title": parsed["title"]})
        return result

    def find(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        if self.vectors is None:
            return []
        results = self.vectors.query(query, limit=limit)
        return [{"document_id": r.get("metadata", {}).get("document_id", ""),
                 "text": r.get("text", ""), "score": r.get("score", 0.0)}
                for r in results if r.get("metadata", {}).get("document_id")]

    def list_documents(self) -> list[str]:
        if self.registry is None:
            return []
        return self.registry.list_documents()

    def get(self, document_id: str) -> dict[str, Any] | None:
        if self.registry is None:
            return None
        document = self.registry.get_document(document_id)
        if document is None:
            return None
        return {"document_id": document.document_id,
                "title": document.title, "content": document.content,
                "file_type": document.file_type,
                "status": document.status.value,
                "tags": list(document.tags),
                "access_level": document.access_level.value}

    def remove(self, document_id: str) -> bool:
        removed = self.manager.remove(document_id)
        if removed:
            self.metrics.increment("ek.documents", -1)
            self.events.publish(EnterpriseKnowledgeEventType.DOCUMENT_REMOVED,
                                {"document_id": document_id})
        return removed

    def stats(self) -> dict[str, Any]:
        return {"documents": len(self.list_documents()),
                "counters": self.metrics.snapshot()["counters"]}
