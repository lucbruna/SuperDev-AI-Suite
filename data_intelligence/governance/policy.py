"""Access policies over datasets."""

from __future__ import annotations

from typing import Any

from data_intelligence.governance.base import PolicyRule


class PolicyManager:
    """Stores and resolves access policy rules."""

    def __init__(self) -> None:
        self.rules: list[PolicyRule] = []

    def add_rule(self, dataset: str, action: str = "allow",
                 operation: str = "*",
                 max_classification: Any = None) -> PolicyRule:
        rule = PolicyRule(dataset=dataset, action=action,
                          operation=operation,
                          max_classification=max_classification)
        self.rules.append(rule)
        return rule

    def rules_for(self, dataset: str, operation: str) -> list[PolicyRule]:
        """Returns the rules that apply to the dataset and operation."""
        matched: list[PolicyRule] = []
        for rule in self.rules:
            if rule.dataset in ("*", dataset) and rule.operation in ("*",
                                                                     operation):
                matched.append(rule)
        return matched

    def stats(self) -> dict[str, Any]:
        return {"rules": len(self.rules),
                "datasets": sorted({r.dataset for r in self.rules
                                    if r.dataset != "*"})}
