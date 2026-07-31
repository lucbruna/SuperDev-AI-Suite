from __future__ import annotations

import logging
import re

from ..knowledge_models import Entity

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "he",
    "her", "his", "in", "is", "it", "its", "of", "on", "or", "our", "she", "the",
    "their", "them", "they", "this", "to", "was", "we", "were", "with", "you",
    "your", "that", "than", "then", "there", "these", "those", "which", "while",
    "who", "will", "would", "into", "over", "under", "about", "after", "before",
}


class EntityExtractor:
    """Extracts candidate entities from text using capitalization heuristics."""

    def __init__(self, min_word_length: int = 3, max_span: int = 3) -> None:
        self._log = logging.getLogger("superdev.knowledge.knowledge_graph.entity_extractor")
        self._min_word_length = min_word_length
        self._max_span = max_span

    def extract(self, text: str, entity_type: str = "concept") -> list[Entity]:
        sentences = re.split(r"[.!?;]\s+", text or "")
        entities: dict[str, Entity] = {}
        for sentence in sentences:
            for match in self._candidates(sentence):
                entities[match] = Entity(name=match, entity_type=entity_type)
        return list(entities.values())

    def _candidates(self, sentence: str) -> list[str]:
        words = re.findall(r"[A-Za-z][A-Za-z0-9_-]*", sentence)
        candidates: list[str] = []
        index = 0
        while index < len(words):
            if self._is_proper_start(words[index]):
                span: list[str] = []
                while index < len(words) and len(span) < self._max_span and self._is_span_word(words[index]):
                    span.append(words[index])
                    index += 1
                candidate = " ".join(span)
                if candidate:
                    candidates.append(candidate)
                continue
            index += 1
        return candidates

    def _is_proper_start(self, word: str) -> bool:
        return word[:1].isupper() and len(word) >= 2 and word.lower() not in _STOPWORDS

    def _is_span_word(self, word: str) -> bool:
        return word[:1].isupper() and len(word) >= 2 and word.lower() not in _STOPWORDS
