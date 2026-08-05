"""AIOS Cognition — perception-to-decision subsystem.

Exposes the cognition engine and its modules: attention, perception,
intent detection, context building, goal management, decision support,
reflection and self evaluation.
"""

from __future__ import annotations

from .attention import Attention
from .cognition_engine import CognitionEngine
from .context_builder import ContextBuilder
from .decision_support import DecisionSupport
from .goal_manager import (
    STATUS_BLOCKED,
    STATUS_COMPLETED,
    STATUS_IN_PROGRESS,
    STATUS_PENDING,
    GoalManager,
)
from .intent_detection import DEFAULT_INTENTS, IntentDetection
from .perception import Perception
from .reflection import Reflection
from .self_evaluation import SelfEvaluation

__all__ = [
    "CognitionEngine",
    "Attention",
    "Perception",
    "IntentDetection",
    "ContextBuilder",
    "GoalManager",
    "DecisionSupport",
    "Reflection",
    "SelfEvaluation",
    "DEFAULT_INTENTS",
    "STATUS_PENDING",
    "STATUS_IN_PROGRESS",
    "STATUS_COMPLETED",
    "STATUS_BLOCKED",
]
