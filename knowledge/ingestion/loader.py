from __future__ import annotations

import logging
from typing import Any

from ..knowledge_models import DocumentRecord, KnowledgeItem


class Loader:
    """Loads raw content from strings and files into title/content pairs."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.ingestion.loader")
        self._supported_extensions = {".txt", ".md", ".rst", ".csv", ".json", ".jsonl"}

    def load_text(self, text: str) -> str:
        return text or ""

    def load_file(self, path: str) -> tuple[str, str]:
        import os

        extension = os.path.splitext(path)[1].lower()
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            content = handle.read()
        if extension not in self._supported_extensions:
            self._log.debug("extension %s not in supported set, loading raw text", extension)
        title = os.path.basename(path)
        return title, content

    def to_document(self, title: str, content: str, doc_type: str = "text",
                    metadata: dict[str, Any] | None = None) -> DocumentRecord:
        return DocumentRecord(
            title=title, content=self.load_text(content), doc_type=doc_type,
            metadata=metadata or {},
        )

    def to_item(self, content: str, kind: str = "text", source: str = "ingestion") -> KnowledgeItem:
        return KnowledgeItem(content=content, kind=kind, source=source)
