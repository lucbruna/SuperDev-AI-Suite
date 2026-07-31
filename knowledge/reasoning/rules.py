from __future__ import annotations

import logging
from dataclasses import dataclass, field


@dataclass
class Rule:
    """A production rule: if all antecedents hold, conclude the consequent."""

    id: str
    antecedents: list[str]
    consequent: str
    confidence: float = 1.0
    metadata: dict[str, str] = field(default_factory=dict)


class RuleSet:
    """Stores and matches production rules against known facts."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.reasoning.rules")
        self._rules: dict[str, Rule] = {}

    def add(self, rule: Rule) -> None:
        self._rules[rule.id] = rule

    def remove(self, rule_id: str) -> bool:
        return self._rules.pop(rule_id, None) is not None

    def get(self, rule_id: str) -> Rule | None:
        return self._rules.get(rule_id)

    def list(self) -> list[Rule]:
        return list(self._rules.values())

    def matching(self, facts: set[str]) -> list[Rule]:
        lowered = {fact.lower() for fact in facts}
        return [
            rule for rule in self._rules.values()
            if all(any(antecedent.lower() in fact for fact in lowered) for antecedent in rule.antecedents)
        ]

    def count(self) -> int:
        return len(self._rules)

    def clear(self) -> None:
        self._rules.clear()
