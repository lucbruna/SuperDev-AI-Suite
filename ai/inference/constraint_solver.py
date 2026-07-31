from __future__ import annotations

from typing import Any


class Constraint:
    """A single constraint with variable, condition, and bound."""

    def __init__(self, name: str, variable: str, condition: str, bound: Any):
        self.name = name
        self.variable = variable
        self.condition = condition
        self.bound = bound


class ConstraintSolver:
    """Constraint satisfaction solver."""

    def __init__(self) -> None:
        self._constraints: list[Constraint] = []

    def add_constraint(self, constraint: Constraint) -> None:
        self._constraints.append(constraint)

    async def solve(self, variables: dict[str, Any]) -> dict[str, Any]:
        solution = dict(variables)
        for constraint in self._constraints:
            if constraint.variable in solution:
                if not self._check(constraint, solution[constraint.variable]):
                    solution[constraint.variable] = constraint.bound
        return solution

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        variables = context.get("variables", {})
        solution = await self.solve(variables)
        return {"solution": solution, "satisfied": self._all_satisfied(solution)}

    def _check(self, constraint: Constraint, value: Any) -> bool:
        if constraint.condition == "eq":
            return value == constraint.bound
        if constraint.condition == "lt":
            return value < constraint.bound
        if constraint.condition == "gt":
            return value > constraint.bound
        if constraint.condition == "lte":
            return value <= constraint.bound
        if constraint.condition == "gte":
            return value >= constraint.bound
        return True

    def _all_satisfied(self, solution: dict[str, Any]) -> bool:
        return all(self._check(c, solution.get(c.variable, c.bound)) for c in self._constraints)
