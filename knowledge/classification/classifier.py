from __future__ import annotations

import logging
from typing import Any

from .category_manager import Category, CategoryManager
from .scorer import Scorer


class Classifier:
    """Classifies text into the best-matching categories."""

    def __init__(self, category_manager: CategoryManager | None = None, scorer: Scorer | None = None) -> None:
        self._log = logging.getLogger("superdev.knowledge.classification.classifier")
        self.category_manager = category_manager or CategoryManager()
        self.scorer = scorer or Scorer()

    def classify(self, text: str, threshold: float = 0.0, top_k: int = 0) -> list[dict[str, Any]]:
        scored = sorted(
            self.scorer.scores(text, self.category_manager.list()).items(),
            key=lambda pair: pair[1],
            reverse=True,
        )
        results = [{"category": name, "score": score} for name, score in scored if score >= threshold]
        if top_k > 0:
            results = results[:top_k]
        return results

    def best(self, text: str) -> dict[str, Any] | None:
        results = self.classify(text)
        return results[0] if results else None
