"""Query suggestions from a known vocabulary."""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.knowledge_protocols import tokenize


class SearchSuggestions:
    """Prefix-based autocomplete over a vocabulary."""

    def __init__(self, vocabulary: list[str] | None = None) -> None:
        self.vocabulary: set[str] = set(vocabulary or [])

    def add(self, *terms: str) -> None:
        for term in terms:
            self.vocabulary.add(term.lower())

    def learn(self, texts: list[str]) -> None:
        for text in texts:
            for token in tokenize(text):
                if len(token) >= 3:
                    self.vocabulary.add(token)

    def suggest(self, prefix: str, limit: int = 5) -> list[str]:
        prefix = prefix.lower()
        if not prefix:
            return []
        matches = [term for term in self.vocabulary
                   if term.startswith(prefix)]
        matches.sort()
        return matches[:max(0, limit)]
