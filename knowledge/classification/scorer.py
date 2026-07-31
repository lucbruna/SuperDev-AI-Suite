from __future__ import annotations

import logging

from .category_manager import Category


class Scorer:
    """Scores text against category keywords using token overlap."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.classification.scorer")

    def score(self, text: str, category: Category) -> float:
        tokens = set(text.lower().split())
        if not tokens:
            return 0.0
        hits = sum(1 for keyword in category.keywords if keyword.lower() in tokens)
        if not category.keywords:
            return 0.0
        return (hits / len(category.keywords)) * category.weight

    def scores(self, text: str, categories: list[Category]) -> dict[str, float]:
        return {category.name: self.score(text, category) for category in categories}
