"""Data models for workflow optimization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class OptimizationSuggestion:
    """A concrete improvement suggestion for a workflow."""

    suggestion_id: str
    target: str  # workflow id or step id
    kind: str    # timeout | fallback | trigger | split | automation
    message: str
    impact: str = ""
    applied: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "suggestion_id": self.suggestion_id,
            "target": self.target,
            "kind": self.kind,
            "message": self.message,
            "impact": self.impact,
            "applied": self.applied,
        }


@dataclass
class OptimizationReport:
    """Analysis result for a single workflow."""

    workflow_id: str
    suggestions: list[OptimizationSuggestion] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "suggestions": [s.to_dict() for s in self.suggestions],
        }
