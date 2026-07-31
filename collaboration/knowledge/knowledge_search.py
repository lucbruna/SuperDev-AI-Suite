"""Wiki search."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_models import KnowledgeRecord


def _normalize(text: str) -> str:
    return (text or "").lower()


class KnowledgeSearch:
    """Searches pages by title, body and tags."""

    def search(self, documents: list[KnowledgeRecord],
               query: str) -> list[KnowledgeRecord]:
        terms = _normalize(query).split()
        if not terms:
            return []
        results = []
        for document in documents:
            haystack = " ".join([
                _normalize(document.title),
                _normalize(document.body),
                " ".join(_normalize(tag) for tag in document.tags),
            ])
            if all(term in haystack for term in terms):
                results.append(document)
        return results

    def by_tag(self, documents: list[KnowledgeRecord],
               tag: str) -> list[KnowledgeRecord]:
        tag = _normalize(tag)
        return [d for d in documents if tag in
                [_normalize(t) for t in d.tags]]

    def by_category(self, categories: Any, category: str,
                    documents: list[KnowledgeRecord],
                    by_id: Any) -> list[KnowledgeRecord]:
        ids = categories.documents_in(category)
        return [doc for doc in documents if doc.document_id in ids]

    def suggest(self, documents: list[KnowledgeRecord],
                prefix: str) -> list[str]:
        prefix = _normalize(prefix)
        titles = []
        for document in documents:
            title = _normalize(document.title)
            if title.startswith(prefix) and title not in titles:
                titles.append(title)
        return titles[:10]
