"""Document record management tied to the registry."""

from __future__ import annotations

import time
from typing import Any

from enterprise_knowledge.knowledge_models import (AccessLevel,
                                                   DocumentRecord,
                                                   DocumentStatus)
from enterprise_knowledge.knowledge_protocols import new_id
from enterprise_knowledge.knowledge_registry import EnterpriseKnowledgeRegistry


class DocumentManager:
    """CRUD over documents; persists only when a registry is provided."""

    def __init__(self, registry: EnterpriseKnowledgeRegistry | None = None,
                 max_title: int = 200) -> None:
        self.registry = registry
        self.max_title = max_title

    def register(self, title: str, content: str = "", source: str = "",
                 file_type: str = "txt", tags: list[str] | None = None,
                 access_level: AccessLevel = AccessLevel.INTERNAL,
                 document_id: str = "") -> DocumentRecord | None:
        if self.registry is None:
            return None
        record = DocumentRecord(
            document_id=document_id or new_id("document"),
            title=title[: self.max_title],
            content=content,
            source=source,
            file_type=file_type,
            tags=list(tags or []),
            status=DocumentStatus.PENDING,
            access_level=access_level,
            created_at=time.time())
        self.registry.register_document(record)
        return record

    def get(self, document_id: str) -> DocumentRecord | None:
        if self.registry is None:
            return None
        return self.registry.get_document(document_id)

    def list(self) -> list[str]:
        if self.registry is None:
            return []
        return self.registry.list_documents()

    def all(self) -> list[DocumentRecord]:
        if self.registry is None:
            return []
        return self.registry.documents()

    def update(self, document_id: str, **changes: Any) -> bool:
        if self.registry is None:
            return False
        record = self.registry.get_document(document_id)
        if record is None:
            return False
        for key, value in changes.items():
            if hasattr(record, key):
                setattr(record, key, value)
        return True

    def set_status(self, document_id: str,
                   status: DocumentStatus) -> bool:
        return self.update(document_id, status=status)

    def remove(self, document_id: str) -> bool:
        if self.registry is None:
            return False
        return self.registry.remove_document(document_id)
