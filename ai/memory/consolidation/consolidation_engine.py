from __future__ import annotations

from typing import Any

from .abstraction import Abstraction
from .concept_merger import ConceptMerger
from .duplication_detector import DuplicationDetector
from .knowledge_merger import KnowledgeMerger
from .learning import Learning
from .pattern_detector import PatternDetector
from .reinforcement import Reinforcement
from .summarizer import Summarizer


class ConsolidationEngine:
    """Facade for memory consolidation — learning, merging, abstraction."""

    def __init__(self):
        self._learning = Learning()
        self._reinforcement = Reinforcement()
        self._patterns = PatternDetector()
        self._duplicates = DuplicationDetector()
        self._summarizer = Summarizer()
        self._abstraction = Abstraction()
        self._knowledge = KnowledgeMerger()
        self._concepts = ConceptMerger()
        self._consolidation_count: int = 0

    @property
    def learning(self) -> Learning:
        return self._learning

    @property
    def reinforcement(self) -> Reinforcement:
        return self._reinforcement

    @property
    def patterns(self) -> PatternDetector:
        return self._patterns

    @property
    def duplicates(self) -> DuplicationDetector:
        return self._duplicates

    @property
    def summarizer(self) -> Summarizer:
        return self._summarizer

    @property
    def abstraction(self) -> Abstraction:
        return self._abstraction

    @property
    def knowledge(self) -> KnowledgeMerger:
        return self._knowledge

    @property
    def concepts(self) -> ConceptMerger:
        return self._concepts

    def consolidate(self, entries: list[dict[str, Any]]) -> dict[str, Any]:
        deduped = self._duplicates.deduplicate(entries)
        summary = self._summarizer.summarize(deduped)
        patterns = self._patterns.detect(deduped)
        abstracted = self._abstraction.create_abstractions(deduped)
        self._consolidation_count += 1
        return {
            "entries": deduped,
            "summary": summary,
            "patterns": patterns,
            "abstractions": abstracted,
            "consolidation_id": self._consolidation_count,
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "consolidation_count": self._consolidation_count,
            "learning_episodes": self._learning.episode_count,
            "reinforcement_cycles": self._reinforcement.cycle_count,
            "patterns_detected": self._patterns.pattern_count,
            "duplicates_found": self._duplicates.duplicate_count,
            "summaries_created": self._summarizer.summary_count,
            "abstractions_created": self._abstraction.abstraction_count,
        }
