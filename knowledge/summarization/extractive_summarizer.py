from __future__ import annotations

import logging
import re

from .sentence_ranker import Sentence


class ExtractiveSummarizer:
    """Builds an extractive summary from ranked sentences."""

    def __init__(self, max_sentences: int = 3, max_chars: int = 500) -> None:
        self._log = logging.getLogger("superdev.knowledge.summarization.extractive_summarizer")
        self.max_sentences = max(1, max_sentences)
        self.max_chars = max(1, max_chars)

    def summarize(self, ranked: list[Sentence]) -> list[Sentence]:
        kept: list[Sentence] = []
        total = 0
        for sentence in sorted(ranked, key=lambda item: item.position):
            if len(kept) >= self.max_sentences:
                break
            if total + len(sentence.text) > self.max_chars:
                continue
            kept.append(sentence)
            total += len(sentence.text)
        return kept

    def split_sentences(self, text: str) -> list[str]:
        parts = re.split(r"(?<=[.!?])\s+", text or "")
        return [part.strip() for part in parts if part.strip()]
