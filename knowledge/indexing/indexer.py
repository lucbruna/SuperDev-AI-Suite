from __future__ import annotations

import logging
from typing import Any

from ..knowledge_models import Chunk, DocumentRecord
from .index_manager import IndexManager


class Indexer:
    """Adds individual documents and chunks to the indexes."""

    def __init__(self, index_manager: IndexManager | None = None) -> None:
        self._log = logging.getLogger("superdev.knowledge.indexing.indexer")
        self.index_manager = index_manager or IndexManager()

    def index_document(self, document: DocumentRecord) -> str:
        document_id = getattr(document, "id", "") or document.title
        self.index_manager.add(document_id, document.content, document.metadata)
        return document_id

    def index_chunk(self, chunk: Chunk) -> str:
        document_id = chunk.document_id or chunk.text[:32]
        self.index_manager.add(document_id, chunk.text, chunk.metadata)
        return document_id

    def index_chunks(self, chunks: list[Chunk]) -> list[str]:
        return [self.index_chunk(chunk) for chunk in chunks]

    def remove(self, document_id: str) -> None:
        self.index_manager.remove(document_id)
