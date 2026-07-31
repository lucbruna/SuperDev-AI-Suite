from __future__ import annotations

import logging
import threading
from typing import Any

from ..knowledge_interfaces import DocumentStore
from ..knowledge_models import DocumentRecord


class InMemoryDocumentManager(DocumentStore):
    """Thread-safe in-memory document store with versioned updates."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.documents.manager")
        self._documents: dict[str, DocumentRecord] = {}
        self._lock = threading.RLock()
        self._next_id = 1

    def add(self, document: DocumentRecord) -> str:
        with self._lock:
            document_id = f"doc-{self._next_id}"
            self._next_id += 1
            self._documents[document_id] = document
            return document_id

    def get(self, document_id: str) -> DocumentRecord | None:
        with self._lock:
            return self._documents.get(document_id)

    def update(self, document_id: str, document: DocumentRecord) -> bool:
        with self._lock:
            if document_id not in self._documents:
                return False
            self._documents[document_id] = document
            return True

    def delete(self, document_id: str) -> bool:
        with self._lock:
            return self._documents.pop(document_id, None) is not None

    def list(self) -> list[DocumentRecord]:
        with self._lock:
            return list(self._documents.values())

    def count(self) -> int:
        with self._lock:
            return len(self._documents)

    def search_title(self, title: str) -> list[DocumentRecord]:
        lowered = title.lower()
        with self._lock:
            return [doc for doc in self._documents.values() if lowered in doc.title.lower()]

    def to_dict(self) -> dict[str, dict[str, Any]]:
        with self._lock:
            return {doc_id: doc.to_dict() for doc_id, doc in self._documents.items()}

    def load_dict(self, data: dict[str, dict[str, Any]]) -> None:
        with self._lock:
            self._documents = {
                doc_id: DocumentRecord(**{k: v for k, v in item.items() if k in DocumentRecord.__dataclass_fields__})
                for doc_id, item in data.items()
            }
