"""Deduction engine for logical reasoning from premises."""
from __future__ import annotations

from typing import Any, Dict, List


class DeductionEngine:
    """Performs deductive reasoning from established premises and rules."""

    def __init__(self) -> None:
        self._deduction_count: int = 0
        self._rules: List[Dict[str, Any]] = []

    def add_rule(self, if_conditions: List[str], then_conclusion: str) -> None:
        self._rules.append({
            "if": list(if_conditions),
            "then": then_conclusion,
        })

    def deduce(self, problem: str, facts: Dict[str, Any]) -> List[Dict[str, Any]]:
        self._deduction_count += 1
        results: List[Dict[str, Any]] = []
        fact_keys = set(facts.keys())
        for rule in self._rules:
            if all(cond in fact_keys for cond in rule["if"]):
                results.append({
                    "rule": rule,
                    "matched_facts": rule["if"],
                    "conclusion": rule["then"],
                    "valid": True,
                })
        problem_words = set(problem.lower().split())
        if "if" in problem_words or "then" in problem_words:
            results.append({
                "rule": {"if": ["problem_structure"], "then": "Conditional logic detected"},
                "matched_facts": [],
                "conclusion": "Problem has conditional structure - apply conditional reasoning",
                "valid": True,
            })
        if not results:
            results.append({
                "rule": {"if": ["default"], "then": "general_analysis"},
                "matched_facts": [],
                "conclusion": "No specific rules matched; apply general analysis",
                "valid": True,
            })
        return results

    def snapshot(self) -> Dict[str, Any]:
        return {"total_deductions": self._deduction_count, "rules": len(self._rules)}
