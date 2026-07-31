"""Learning subsystem for adaptive improvement and knowledge transfer."""

from __future__ import annotations

from .adaptation import AdaptationEngine
from .experience_replay import ExperienceReplay
from .knowledge_sharing import KnowledgeSharing
from .learning_engine import LearningEngine
from .meta_learning import MetaLearner
from .transfer import TransferLearning

__all__ = [
    "LearningEngine",
    "TransferLearning",
    "AdaptationEngine",
    "KnowledgeSharing",
    "ExperienceReplay",
    "MetaLearner",
]
