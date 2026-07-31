from __future__ import annotations

import logging
from typing import Any

from ..knowledge_models import DocumentRecord
from .ingestion_engine import IngestionEngine
from .loader import Loader
from .tracker import IngestionTracker


class IngestionManager:
    """High-level facade for ingesting content from text, files, and documents."""

    def __init__(self, engine: IngestionEngine | None = None) -> None:
        self._log = logging.getLogger("superdev.knowledge.ingestion.manager")
        self.engine = engine or IngestionEngine()
        self.loader = Loader()
        self.tracker = self.engine.tracker

    def ingest_text(self, title: str, content: str, doc_type: str = "text",
                    metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        document = self.loader.to_document(title, content, doc_type=doc_type, metadata=metadata)
        return self.engine.ingest_document(document)

    def ingest_file(self, path: str, doc_type: str = "text",
                    metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        title, content = self.loader.load_file(path)
        document = self.loader.to_document(title, content, doc_type=doc_type, metadata=metadata)
        return self.engine.ingest_document(document)

    def ingest_batch(self, documents: list[DocumentRecord]) -> dict[str, Any]:
        return self.engine.ingest_batch(documents)

    def status(self, document_id: str) -> str | None:
        return self.tracker.status(document_id)

    def stats(self) -> dict[str, Any]:
        return self.engine.stats()
