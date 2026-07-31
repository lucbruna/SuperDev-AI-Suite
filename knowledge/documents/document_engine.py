from __future__ import annotations

import logging
from typing import Any

from ..knowledge_config import KnowledgeConfig
from ..knowledge_events import KnowledgeEvents, KnowledgeEventType
from ..knowledge_interfaces import DocumentStore
from ..knowledge_metrics import KnowledgeMetrics
from ..knowledge_models import DocumentRecord
from .document_manager import InMemoryDocumentManager
from .metadata import DocumentMetadata
from .parser import Parser
from .versioning import DocumentVersioning


class DocumentEngine:
    """Composes document parsing, storage, and versioning."""

    def __init__(
        self,
        store: DocumentStore | None = None,
        config: KnowledgeConfig | None = None,
        events: KnowledgeEvents | None = None,
        metrics: KnowledgeMetrics | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.documents.engine")
        self.config = config or KnowledgeConfig()
        self.events = events or KnowledgeEvents()
        self.metrics = metrics or KnowledgeMetrics()
        self.store = store or InMemoryDocumentManager()
        self.parser = Parser()
        self.metadata_builder = DocumentMetadata()
        self.versioning = DocumentVersioning()

    def add_document(self, document: DocumentRecord) -> str:
        document_id = self.store.add(document)
        self.versioning.snapshot(document_id, document.content, document.version)
        self.metrics.increment("documents.engine.added")
        self.events.emit(KnowledgeEventType.DOCUMENT_ADDED, {"document_id": document_id})
        return document_id

    def parse_file(self, path: str) -> DocumentRecord:
        document = self.parser.parse(path)
        self.metrics.increment("documents.engine.parsed")
        return document

    def add_file(self, path: str) -> str:
        document = self.parse_file(path)
        return self.add_document(document)

    def get(self, document_id: str) -> DocumentRecord | None:
        return self.store.get(document_id)

    def update(self, document_id: str, document: DocumentRecord) -> bool:
        document.version += 1
        updated = self.store.update(document_id, document)
        if updated:
            self.versioning.snapshot(document_id, document.content, document.version)
            self.events.emit(KnowledgeEventType.DOCUMENT_UPDATED, {"document_id": document_id})
        return updated

    def stats(self) -> dict[str, Any]:
        return {"documents": len(self.store.list())}
