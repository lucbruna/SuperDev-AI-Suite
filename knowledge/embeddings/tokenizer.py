from __future__ import annotations

import logging
import re
from collections import Counter


class Tokenizer:
    """Splits text into normalized tokens."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.embeddings.tokenizer")
        self._pattern = re.compile(r"[a-zA-Z0-9_]+")

    def tokenize(self, text: str) -> list[str]:
        return [token.lower() for token in self._pattern.findall(text)]

    def vocabulary(self, texts: list[str]) -> dict[str, int]:
        counter: Counter[str] = Counter()
        for text in texts:
            counter.update(self.tokenize(text))
        return dict(counter)

    def bag_of_words(self, text: str, vocabulary: dict[str, int] | None = None) -> dict[str, int]:
        counts = Counter(self.tokenize(text))
        if vocabulary is not None:
            return {word: counts.get(word, 0) for word in vocabulary}
        return dict(counts)
