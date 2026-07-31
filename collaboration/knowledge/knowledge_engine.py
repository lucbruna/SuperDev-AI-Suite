"""Knowledge engine: wiki colaborativa.

Equipe documenta arquitetura, processos e decisões; agentes de IA
ajudam a redigir e revisar páginas.
"""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_config import CollaborationConfig
from collaboration.collaboration_events import (CollaborationEventType,
                                                CollaborationEvents)
from collaboration.collaboration_logger import get_logger
from collaboration.collaboration_metrics import CollaborationMetrics
from collaboration.collaboration_models import KnowledgeRecord
from collaboration.collaboration_registry import CollaborationRegistry
from collaboration.collaboration_security import CollaborationSecurity
from collaboration.knowledge.knowledge_manager import KnowledgeManager


class KnowledgeEngine:
    """Orquestrador da wiki (Fase 7 do Volume 26)."""

    def __init__(self, events: CollaborationEvents | None = None,
                 metrics: CollaborationMetrics | None = None,
                 config: CollaborationConfig | None = None,
                 security: CollaborationSecurity | None = None,
                 registry: CollaborationRegistry | None = None,
                 manager: KnowledgeManager | None = None) -> None:
        self._log = get_logger()
        self.events = events or CollaborationEvents()
        self.metrics = metrics or CollaborationMetrics()
        self.config = config or CollaborationConfig()
        self.security = security or CollaborationSecurity()
        self.manager = manager or KnowledgeManager(registry=registry)

    def create(self, workspace_id: str, title: str, body: str,
               author_id: str = "", tags: list[str] | None = None,
               category: str = "") -> KnowledgeRecord:
        document = self.manager.create(workspace_id, title, body,
                                       author_id, tags, category)
        self.metrics.increment("collab.documents")
        self.events.publish(CollaborationEventType.DOCUMENT_CREATED,
                            {"document_id": document.document_id,
                             "title": title,
                             "workspace_id": workspace_id})
        return document

    def get(self, document_id: str) -> KnowledgeRecord | None:
        return self.manager.get(document_id)

    def list(self) -> list[str]:
        return self.manager.list()

    def remove(self, document_id: str) -> bool:
        return self.manager.remove(document_id)

    def edit(self, document_id: str, body: str, editor_id: str,
             tags: list[str] | None = None) -> KnowledgeRecord | None:
        document = self.manager.edit(document_id, body, editor_id, tags)
        if document is not None:
            self.events.publish(CollaborationEventType.DOCUMENT_UPDATED,
                                {"document_id": document_id,
                                 "version": document.version,
                                 "editor_id": editor_id})
        return document

    def history(self, document_id: str) -> Any:
        return self.manager.history(document_id)

    def search(self, query: str) -> list[KnowledgeRecord]:
        return self.manager.search_documents(query)

    def by_tag(self, tag: str) -> list[KnowledgeRecord]:
        return self.manager.search.by_tag(self.manager.all_records(), tag)

    def categories(self) -> dict[str, int]:
        return self.manager.categories.counts()

    def add_category(self, name: str) -> bool:
        return self.manager.categories.add(name)

    def category_documents(self, category: str) -> list[str]:
        return self.manager.categories.documents_in(category)

    def stats(self) -> dict[str, Any]:
        return {"documents": self.manager.count(),
                "categories": len(self.manager.categories.list())}
