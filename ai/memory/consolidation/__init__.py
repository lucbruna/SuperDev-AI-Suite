from __future__ import annotations

from .consolidation_engine import ConsolidationEngine
from .learning import Learning
from .reinforcement import Reinforcement
from .pattern_detector import PatternDetector
from .duplication_detector import DuplicationDetector
from .summarizer import Summarizer
from .abstraction import Abstraction
from .knowledge_merger import KnowledgeMerger
from .concept_merger import ConceptMerger

__all__ = [
    "ConsolidationEngine",
    "Learning",
    "Reinforcement",
    "PatternDetector",
    "DuplicationDetector",
    "Summarizer",
    "Abstraction",
    "KnowledgeMerger",
    "ConceptMerger",
]
