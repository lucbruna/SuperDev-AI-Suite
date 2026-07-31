from __future__ import annotations

from typing import Literal, TypedDict

DecisionPhase: type = Literal[
    "pending",
    "analyzing",
    "selecting",
    "executing",
    "validating",
    "completed",
    "failed",
]


class DecisionCriteriaDict(TypedDict, total=False):
    urgency: float
    impact: float
    effort: float
    risk: float
    confidence_threshold: float
