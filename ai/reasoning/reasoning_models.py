from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ReasoningResult:
    """Result of a reasoning operation."""

    decision: str
    confidence: float = 0.0
    context_id: str = ""
    reasoning_path: list[str] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class Hypothesis:
    """A generated hypothesis for evaluation."""

    statement: str
    confidence: float = 0.0
    evidence: list[str] = field(default_factory=list)
    source: str = ""


@dataclass
class DecisionPath:
    """A chain of reasoning steps leading to a decision."""

    steps: list[dict[str, Any]] = field(default_factory=list)
    final_decision: str = ""
    confidence: float = 0.0
