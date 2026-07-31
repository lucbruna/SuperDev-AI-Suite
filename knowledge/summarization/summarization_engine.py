from __future__ import annotations

import logging
from typing import Any

from ..knowledge_config import KnowledgeConfig
from ..knowledge_events import KnowledgeEvents, KnowledgeEventType
from ..knowledge_metrics import KnowledgeMetrics
from .extractive_summarizer import ExtractiveSummarizer
from .sentence_ranker import SentenceRanker
from .summary_builder import SummaryBuilder


class SummarizationEngine:
    """Composes sentence ranking and extractive summarization."""

    def __init__(
        self,
        config: KnowledgeConfig | None = None,
        events: KnowledgeEvents | None = None,
        metrics: KnowledgeMetrics | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.summarization.engine")
        self.config = config or KnowledgeConfig()
        self.events = events or KnowledgeEvents()
        self.metrics = metrics or KnowledgeMetrics()
        self.sentence_ranker = SentenceRanker()
        self.builder = SummaryBuilder(self.sentence_ranker, ExtractiveSummarizer())

    def summarize(self, text: str) -> dict[str, Any]:
        result = self.builder.build(text)
        self.metrics.increment("summarization.executed")
        self.events.emit(KnowledgeEventType.EMBEDDING_CREATED, {"summary_length": len(result["summary"])})
        return result

    def stats(self) -> dict[str, Any]:
        return {"summary_max_sentences": self.builder.extractive.max_sentences}
