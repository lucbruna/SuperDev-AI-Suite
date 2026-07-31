from __future__ import annotations

import logging
from typing import Any


class MetadataIndex:
    """Indexes documents by arbitrary metadata keys for filtered lookups."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.indexing.metadata_index")
        self._entries: dict[str, dict[str, Any]] = {}

    def add(self, document_id: str, metadata: dict[str, Any] | None = None) -> None:
        self._entries[document_id] = dict(metadata or {})

    def get(self, document_id: str) -> dict[str, Any]:
        return self._entries.get(document_id, {})

    def filter(self, metadata_eq: dict[str, Any] | None = None) -> list[str]:
        if not metadata_eq:
            return list(self._entries.keys())
        return [
            document_id
            for document_id, metadata in self._entries.items()
            if all(metadata.get(key) == value for key, value in metadata_eq.items())
        ]

    def remove(self, document_id: str) -> None:
        self._entries.pop(document_id, None)

    def count(self) -> int:
        return len(self._entries)

    def clear(self) -> None:
        self._entries.clear()
