from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class DecisionContext:
    """Context for a decision-making process."""

    options: list[str] = field(default_factory=list)
    context_id: str = ""
    criteria: dict[str, Any] = field(default_factory=dict)
    constraints: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "options": self.options,
            "criteria": self.criteria,
            "constraints": self.constraints,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }
