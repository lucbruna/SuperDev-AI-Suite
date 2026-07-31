"""Forward-chaining inference over simple IF-THEN rules."""

from __future__ import annotations

from typing import Any


class InferenceEngine:
    """Applies rules against known facts to derive new conclusions."""

    def __init__(self) -> None:
        self.rules: list[dict[str, Any]] = []

    def add_rule(self, antecedent: list[str], consequent: str,
                 confidence: float = 0.8) -> None:
        self.rules.append({"antecedent": [str(a).lower() for a in antecedent],
                           "consequent": consequent,
                           "confidence": max(0.0, min(1.0, confidence))})

    def infer(self, facts: list[str], max_steps: int = 5) -> list[dict[str, Any]]:
        known = {fact.lower() for fact in facts}
        conclusions: list[dict[str, Any]] = []
        changed = True
        steps = 0
        while changed and steps < max_steps:
            changed = False
            steps += 1
            for rule in self.rules:
                matched = all(
                    any(antecedent in fact for fact in known)
                    for antecedent in rule["antecedent"])
                if not matched or rule["consequent"].lower() in known:
                    continue
                known.add(rule["consequent"].lower())
                conclusions.append({"conclusion": rule["consequent"],
                                    "confidence": rule["confidence"]})
                changed = True
        return conclusions

    def rules_count(self) -> int:
        return len(self.rules)
