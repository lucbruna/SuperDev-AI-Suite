"""AIOS Logical Reasoning — deductive inference.

Applies modus ponens / syllogism-style deduction over premises given
as dicts with "if"/"then" or implication structures.
"""

from __future__ import annotations

from typing import Any


class LogicalReasoning:
    """Rule-based deductive reasoning."""

    def reason(self, premises: list[Any], **kwargs: Any) -> dict[str, Any]:
        conclusions: list[str] = []
        steps: list[str] = []
        for premise in premises:
            if isinstance(premise, dict) and "if" in premise and "then" in premise:
                condition = str(premise["if"]).lower()
                conclusion = str(premise["then"])
                facts = {str(f).lower() for f in kwargs.get("facts", [])}
                if condition in facts:
                    conclusions.append(conclusion)
                    steps.append(f"modus ponens: {premise['if']} -> {conclusion}")
                else:
                    steps.append(f"condition not satisfied: {condition}")
            elif isinstance(premise, dict) and "all" in premise and "is" in premise:
                # Syllogism: all X are Y; given x is X => x is Y
                all_class = str(premise["all"])
                y = str(premise["is"])
                for fact in kwargs.get("facts", []):
                    if isinstance(fact, str) and all_class.lower() in fact.lower():
                        conclusions.append(f"{fact} is {y}")
                        steps.append(f"syllogism: all {all_class} are {y}")
        return {
            "ok": True,
            "strategy": "logical",
            "conclusions": conclusions,
            "steps": steps,
        }
