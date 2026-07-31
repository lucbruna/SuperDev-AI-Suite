"""Learning subsystem for adaptive improvement and knowledge transfer."""
from __future__ import annotations

from .learning_engine import LearningEngine
from .transfer import TransferLearning
from .adaptation import AdaptationEngine
from .knowledge_sharing import KnowledgeSharing
from .experience_replay import ExperienceReplay
from .meta_learning import MetaLearner

__all__ = [
    "LearningEngine",
    "TransferLearning",
    "AdaptationEngine",
    "KnowledgeSharing",
    "ExperienceReplay",
    "MetaLearner",
]
