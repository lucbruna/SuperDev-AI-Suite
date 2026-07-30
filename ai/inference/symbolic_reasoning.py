from __future__ import annotations

from typing import Any

from .predicate_logic import PredicateLogic
from .rule_engine import RuleEngine


class SymbolicReasoning:
    """Symbolic reasoning using rules and predicate logic."""

    def __init__(
        self,
        rule_engine: RuleEngine | None = None,
        predicate_logic: PredicateLogic | None = None,
    ):
        self._rule_engine = rule_engine or RuleEngine()
        self._predicate_logic = predicate_logic or PredicateLogic()

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        facts = context.get("facts", [])
        rules = context.get("rules", [])
        derived = await self._rule_engine.apply(rules, facts)
        validated = await self._predicate_logic.validate(derived)
        return {"derived": derived, "validated": validated, "confidence": 0.9}

    async def forward_chain(self, facts: list[Any], rules: list[Any]) -> list[Any]:
        return await self._rule_engine.forward_chain(facts, rules)

    async def backward_chain(self, goal: Any, rules: list[Any]) -> list[Any]:
        return await self._rule_engine.backward_chain(goal, rules)
