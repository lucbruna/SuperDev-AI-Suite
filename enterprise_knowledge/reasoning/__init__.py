"""Reasoning subsystem (Volume 27, Fase 8)."""

from __future__ import annotations

from .explanation import ExplanationGenerator
from .hypothesis import HypothesisGenerator
from .inference import InferenceEngine
from .reasoning_engine import ReasoningEngine
from .recommendation import RecommendationEngine

__all__ = [
    "ExplanationGenerator",
    "HypothesisGenerator",
    "InferenceEngine",
    "ReasoningEngine",
    "RecommendationEngine",
]
