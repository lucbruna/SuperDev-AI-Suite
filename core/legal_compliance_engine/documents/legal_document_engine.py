"""
Legal Document Engine - Core document management coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..legal_context import LegalContext
from ..legal_events import LegalEvent, LegalEventBus, EventType
from ..legal_models import LegalDocument, DocumentType
from ..legal_config import LegalConfig
from .document_classifier import DocumentClassifier
from .document_search import DocumentSearch
from .document_summary import DocumentSummary
from .archive_manager import ArchiveManager

logger = logging.getLogger(__name__)


class LegalDocumentEngine:
    def __init__(self, config: LegalConfig, context: LegalContext, event_bus: LegalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.classifier: Optional[DocumentClassifier] = None
        self.search: Optional[DocumentSearch] = None
        self.summary: Optional[DocumentSummary] = None
        self.archive: Optional[ArchiveManager] = None

    async def initialize(self) -> None:
        self.classifier = DocumentClassifier(self.config, self.context, self.event_bus)
        self.search = DocumentSearch(self.config, self.context, self.event_bus)
        self.summary = DocumentSummary(self.config, self.context, self.event_bus)
        self.archive = ArchiveManager(self.config, self.context, self.event_bus)
        logger.info("LegalDocumentEngine initialized")

    async def get_document(self, document_id: str) -> LegalDocument:
        return LegalDocument(id=document_id, title="Sample Document")

    async def classify_document(self, doc: LegalDocument) -> LegalDocument:
        await self.event_bus.publish(LegalEvent(
            event_type=EventType.DOCUMENT_CLASSIFIED,
            payload={"document_id": doc.id, "type": doc.document_type.value},
        ))
        return doc

    async def shutdown(self) -> None:
        logger.info("LegalDocumentEngine shutdown")
