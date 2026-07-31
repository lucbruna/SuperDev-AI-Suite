"""Wiki categories (áreas da base de conhecimento)."""

from __future__ import annotations

from typing import Any

DEFAULT_CATEGORIES = [
    "Arquitetura",
    "Processos",
    "DevOps",
    "Segurança",
    "Negócio",
    "Decisões",
]


class KnowledgeCategories:
    """Manages the category tree of the collaborative wiki."""

    def __init__(self) -> None:
        self._categories: dict[str, dict[str, Any]] = {
            name: {"name": name, "documents": []}
            for name in DEFAULT_CATEGORIES
        }

    def add(self, name: str) -> bool:
        if name in self._categories:
            return False
        self._categories[name] = {"name": name, "documents": []}
        return True

    def remove(self, name: str) -> bool:
        if name not in self._categories:
            return False
        del self._categories[name]
        return True

    def list(self) -> list[str]:
        return list(self._categories)

    def assign(self, name: str, document_id: str) -> bool:
        category = self._categories.get(name)
        if category is None:
            return False
        if document_id not in category["documents"]:
            category["documents"].append(document_id)
        return True

    def documents_in(self, name: str) -> list[str]:
        category = self._categories.get(name)
        return list(category["documents"]) if category else []

    def counts(self) -> dict[str, int]:
        return {name: len(cat["documents"])
                for name, cat in self._categories.items()}
