from __future__ import annotations

import logging
from typing import Any

from .rules import Rule, RuleSet


class Inference:
    """Forward-chaining inference engine over facts and rules."""

    def __init__(self, rules: RuleSet | None = None) -> None:
        self._log = logging.getLogger("superdev.knowledge.reasoning.inference")
        self.rules = rules or RuleSet()
        self._facts: set[str] = set()

    def add_fact(self, fact: str) -> None:
        self._facts.add(fact)

    def add_facts(self, facts: list[str]) -> None:
        self._facts.update(fact for fact in facts if fact)

    def add_rule(self, rule: Rule) -> None:
        self.rules.add(rule)

    def infer(self, max_iterations: int = 10) -> list[str]:
        derived: set[str] = set()
        for _ in range(max(1, max_iterations)):
            changed = False
            for rule in self.rules.matching(self._facts):
                consequent = rule.consequent
                if consequent not in derived:
                    derived.add(consequent)
                    changed = True
            self._facts.update(derived)
            if not changed:
                break
        self._log.debug("inferred %d facts", len(derived))
        return sorted(derived)

    def facts(self) -> list[str]:
        return sorted(self._facts)

    def reset(self) -> None:
        self._facts.clear()
