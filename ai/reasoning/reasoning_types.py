from __future__ import annotations

from typing import Literal, TypedDict

ReasoningPhase: type = Literal[
    "idle",
    "analyzing",
    "generating",
    "evaluating",
    "deciding",
    "validating",
    "completed",
    "failed",
]
ConfidenceLevel: type = Literal["low", "medium", "high", "certain"]


class ReasoningStepDict(TypedDict, total=False):
    step: int
    phase: str
    hypothesis: str
    confidence: float
    duration_ms: float
    timestamp: str


class EvaluationResultDict(TypedDict, total=False):
    score: float
    confidence: float
    rationale: str
    risks: list[str]
