from __future__ import annotations

import logging
from collections import Counter
from typing import Any

from ..knowledge_models import Chunk, DocumentRecord


class InvertedIndex:
    """Keyword index mapping tokens to document frequencies."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.indexing.inverted_index")
        self._postings: dict[str, dict[str, int]] = {}

    def add(self, document_id: str, text: str) -> None:
        tokens = Counter(word for word in text.lower().split() if word)
        for token, count in tokens.items():
            postings = self._postings.setdefault(token, {})
            postings[document_id] = postings.get(document_id, 0) + count

    def remove(self, document_id: str) -> None:
        for postings in self._postings.values():
            postings.pop(document_id, None)

    def search(self, query: str) -> list[tuple[str, float]]:
        tokens = {word for word in query.lower().split() if word}
        scores: dict[str, float] = {}
        for token in tokens:
            for document_id, count in self._postings.get(token, {}).items():
                scores[document_id] = scores.get(document_id, 0.0) + count
        return sorted(scores.items(), key=lambda pair: pair[1], reverse=True)

    def count(self) -> int:
        return len(self._postings)

    def clear(self) -> None:
        self._postings.clear()
