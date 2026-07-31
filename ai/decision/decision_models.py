from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class DecisionResult:
    """Result of a decision operation."""

    decision: str
    confidence: float = 0.0
    context_id: str = ""
    alternatives: list[str] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class DecisionOption:
    """A single option in a decision process."""

    label: str
    value: Any = None
    score: float = 0.0
    confidence: float = 0.0
