"""Data models for business rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class RuleDefinition:
    """A rule with a condition and a consequence."""

    rule_id: str
    name: str
    condition: dict[str, Any] | None = None  # declarative condition
    predicate: Callable[[dict[str, Any]], bool] | None = None
    action: Callable[[dict[str, Any]], Any] | None = None  # consequence
    params: dict[str, Any] = field(default_factory=dict)
    priority: int = 0  # higher runs first
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "condition": self.condition,
            "priority": self.priority,
            "enabled": self.enabled,
        }


@dataclass
class RuleResult:
    """Outcome of evaluating a rule against facts."""

    rule_id: str
    matched: bool
    consequence: Any = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"rule_id": self.rule_id, "matched": self.matched,
                "consequence": self.consequence, "error": self.error}
