from __future__ import annotations

import logging
from dataclasses import dataclass, field


@dataclass
class Category:
    """A labeled category with scoring keywords."""

    name: str
    keywords: list[str] = field(default_factory=list)
    weight: float = 1.0

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "keywords": list(self.keywords), "weight": self.weight}


class CategoryManager:
    """Stores and retrieves classification categories."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.classification.category_manager")
        self._categories: dict[str, Category] = {}

    def add(self, category: Category) -> None:
        self._categories[category.name] = category

    def remove(self, name: str) -> bool:
        return self._categories.pop(name, None) is not None

    def get(self, name: str) -> Category | None:
        return self._categories.get(name)

    def list(self) -> list[Category]:
        return list(self._categories.values())

    def names(self) -> list[str]:
        return list(self._categories.keys())

    def clear(self) -> None:
        self._categories.clear()
