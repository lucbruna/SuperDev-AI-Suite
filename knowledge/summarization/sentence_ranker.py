from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass, field


@dataclass
class Sentence:
    """A scored sentence candidate for extractive summarization."""

    text: str
    score: float = 0.0
    position: int = 0

    def to_dict(self) -> dict[str, object]:
        return {"text": self.text, "score": self.score, "position": self.position}


class SentenceRanker:
    """Ranks sentences by term-frequency salience."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.summarization.sentence_ranker")

    def rank(self, sentences: list[str]) -> list[Sentence]:
        if not sentences:
            return []
        frequencies = self._frequencies(sentences)
        total = sum(frequencies.values()) or 1
        scored = []
        for position, text in enumerate(sentences):
            tokens = [word for word in text.lower().split() if word]
            score = sum(frequencies.get(word, 0) for word in tokens) / total
            scored.append(Sentence(text=text, score=score, position=position))
        return sorted(scored, key=lambda sentence: sentence.score, reverse=True)

    def _frequencies(self, sentences: list[str]) -> Counter[str]:
        counter: Counter[str] = Counter()
        for sentence in sentences:
            counter.update(word for word in sentence.lower().split() if word)
        return counter
