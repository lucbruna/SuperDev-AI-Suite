from __future__ import annotations

import logging
from typing import Any

from .extractive_summarizer import ExtractiveSummarizer
from .sentence_ranker import Sentence, SentenceRanker


class SummaryBuilder:
    """Composes sentence splitting, ranking, and extractive selection."""

    def __init__(
        self,
        sentence_ranker: SentenceRanker | None = None,
        extractive: ExtractiveSummarizer | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.summarization.summary_builder")
        self.sentence_ranker = sentence_ranker or SentenceRanker()
        self.extractive = extractive or ExtractiveSummarizer()

    def build(self, text: str) -> dict[str, Any]:
        sentences = self.extractive.split_sentences(text)
        ranked = self.sentence_ranker.rank(sentences)
        selected = self.extractive.summarize(ranked)
        summary_text = " ".join(sentence.text for sentence in selected)
        return {
            "summary": summary_text,
            "sentences": [sentence.to_dict() for sentence in selected],
            "total_sentences": len(sentences),
            "compression": self._compression(text, summary_text),
        }

    def _compression(self, original: str, summary: str) -> float:
        if not original:
            return 0.0
        return 1.0 - (len(summary) / len(original))
