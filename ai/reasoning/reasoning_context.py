from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ReasoningContext:
    """Context for a reasoning session."""

    query: str = ""
    context_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    constraints: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def add_constraint(self, constraint: str) -> None:
        self.constraints.append(constraint)

    def to_dict(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "query": self.query,
            "metadata": self.metadata,
            "constraints": self.constraints,
            "created_at": self.created_at,
        }
