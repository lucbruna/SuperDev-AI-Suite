"""Wiki lifecycle management."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_models import KnowledgeRecord
from collaboration.knowledge.knowledge_categories import KnowledgeCategories
from collaboration.knowledge.knowledge_history import VersionHistory
from collaboration.knowledge.knowledge_pages import KnowledgePage
from collaboration.knowledge.knowledge_search import KnowledgeSearch


class KnowledgeManager:
    """CRUD for wiki pages plus categories, history and search."""

    def __init__(self, registry: Any = None) -> None:
        self.registry = registry
        self.categories = KnowledgeCategories()
        self.search = KnowledgeSearch()
        self._history: dict[str, VersionHistory] = {}
        self._pages: dict[str, KnowledgePage] = {}

    def create(self, workspace_id: str, title: str, body: str,
               author_id: str = "", tags: list[str] | None = None,
               category: str = "") -> KnowledgeRecord:
        page = KnowledgePage(workspace_id, title, body, author_id,
                             tags or [])
        self._pages[page.record.document_id] = page
        if self.registry is not None:
            self.registry.register_document(page.record.document_id,
                                            page.record)
        history = VersionHistory()
        history.snapshot(page.record.document_id, 1, title, body,
                         author_id)
        self._history[page.record.document_id] = history
        if category:
            self.categories.assign(category, page.record.document_id)
        return page.record

    def get(self, document_id: str) -> KnowledgeRecord | None:
        page = self._pages.get(document_id)
        return page.record if page is not None else None

    def list(self) -> list[str]:
        return list(self._pages)

    def remove(self, document_id: str) -> bool:
        removed = self._pages.pop(document_id, None) is not None
        self._history.pop(document_id, None)
        if removed and self.registry is not None:
            return self.registry.remove_document(document_id)
        return removed

    def edit(self, document_id: str, body: str, editor_id: str,
             tags: list[str] | None = None) -> KnowledgeRecord | None:
        page = self._pages.get(document_id)
        if page is None:
            return None
        version = page.edit(body, editor_id, tags)
        self._history[document_id].snapshot(
            document_id, version, page.record.title, body, editor_id)
        return page.record

    def history(self, document_id: str) -> VersionHistory:
        history = self._history.get(document_id)
        if history is None:
            history = VersionHistory()
            self._history[document_id] = history
        return history

    def all_records(self) -> list[KnowledgeRecord]:
        return [page.record for page in self._pages.values()]

    def search_documents(self, query: str) -> list[KnowledgeRecord]:
        return self.search.search(self.all_records(), query)

    def count(self) -> int:
        return len(self._pages)
