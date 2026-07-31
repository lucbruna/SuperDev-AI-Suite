from __future__ import annotations

import logging
from typing import Any

from .inverted_index import InvertedIndex
from .metadata_index import MetadataIndex


class IndexManager:
    """Manages the family of indexes (keyword, metadata, custom)."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.indexing.index_manager")
        self.keyword = InvertedIndex()
        self.metadata = MetadataIndex()
        self._custom: dict[str, Any] = {}

    def register(self, name: str, index: Any) -> None:
        self._custom[name] = index

    def get(self, name: str) -> Any | None:
        return self._custom.get(name)

    def names(self) -> list[str]:
        return list(self._custom.keys())

    def add(self, document_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        self.keyword.add(document_id, text)
        self.metadata.add(document_id, metadata)
        for index in self._custom.values():
            if hasattr(index, "add"):
                index.add(document_id, text)

    def remove(self, document_id: str) -> None:
        self.keyword.remove(document_id)
        self.metadata.remove(document_id)
        for index in self._custom.values():
            if hasattr(index, "remove"):
                index.remove(document_id)

    def stats(self) -> dict[str, Any]:
        return {
            "keyword_terms": self.keyword.count(),
            "metadata_documents": self.metadata.count(),
            "custom": list(self._custom.keys()),
        }

    def clear(self) -> None:
        self.keyword.clear()
        self.metadata.clear()
        self._custom.clear()
