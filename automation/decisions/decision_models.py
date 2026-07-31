"""Data models for decision trees."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DecisionBranch:
    """A conditional transition from a decision node."""

    branch_id: str
    condition: dict[str, Any]  # declarative condition (see TriggerEvaluator)
    target: str  # node id or action

    def to_dict(self) -> dict[str, Any]:
        return {"branch_id": self.branch_id,
                "condition": self.condition, "target": self.target}


@dataclass
class DecisionNode:
    """A question with branches, or a leaf that performs an action."""

    node_id: str
    question: str = ""
    branches: list[DecisionBranch] = field(default_factory=list)
    action: str | None = None  # leaf: action to execute
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"node_id": self.node_id,
                "question": self.question,
                "branches": [b.to_dict() for b in self.branches],
                "action": self.action}


@dataclass
class DecisionResult:
    """Outcome of walking a decision tree."""

    tree_id: str
    decision: str
    path: list[str] = field(default_factory=list)
    action: str | None = None
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"tree_id": self.tree_id,
                "decision": self.decision,
                "path": list(self.path),
                "action": self.action}
