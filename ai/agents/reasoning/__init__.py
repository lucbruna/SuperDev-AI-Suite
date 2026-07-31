"""Reasoning subsystem - inference, deduction, decision making."""
from __future__ import annotations

from .reasoning_engine import ReasoningEngine
from .inference import InferenceEngine
from .deduction import DeductionEngine
from .evaluation import ReasoningEvaluator
from .decision import DecisionEngine
from .hypothesis import HypothesisManager
from .verification import VerificationEngine

__all__ = [
    "ReasoningEngine", "InferenceEngine", "DeductionEngine",
    "ReasoningEvaluator", "DecisionEngine", "HypothesisManager",
    "VerificationEngine",
]
