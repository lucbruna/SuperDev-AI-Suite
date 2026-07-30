from __future__ import annotations

from typing import Any


class Predicate:
    """A logical predicate with name and arguments."""

    def __init__(self, name: str, arguments: list[Any] | None = None):
        self.name = name
        self.arguments = arguments or []

    def evaluate(self, facts: list[Any]) -> bool:
        return any(self.name == f.get("name") and self.arguments == f.get("arguments") for f in facts)


class PredicateLogic:
    """Predicate logic evaluation and validation."""

    def __init__(self) -> None:
        self._predicates: dict[str, Predicate] = {}

    def register(self, predicate: Predicate) -> None:
        self._predicates[predicate.name] = predicate

    async def evaluate(self, expression: dict[str, Any], facts: list[Any]) -> bool:
        op = expression.get("operator")
        if op == "and":
            results = [await self.evaluate(e, facts) for e in expression.get("operands", [])]
            return all(results)
        if op == "or":
            results = [await self.evaluate(e, facts) for e in expression.get("operands", [])]
            return any(results)
        if op == "not":
            return not await self.evaluate(expression.get("operand", {}), facts)
        predicate_name = expression.get("predicate", "")
        predicate = self._predicates.get(predicate_name)
        if predicate is None:
            return False
        return predicate.evaluate(facts)

    async def validate(self, facts: list[Any]) -> list[Any]:
        return [f for f in facts if isinstance(f, dict)]
