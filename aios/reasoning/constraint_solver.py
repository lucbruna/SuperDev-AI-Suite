"""AIOS Constraint Solver — small CSP with backtracking.

Variables with domains plus binary inequality constraints; solves via
deterministic backtracking (MRV heuristic).
"""

from __future__ import annotations

from typing import Any


class ConstraintSolver:
    """Backtracking solver for small constraint satisfaction problems."""

    def __init__(self) -> None:
        self._domains: dict[str, list[Any]] = {}
        self._constraints: list[tuple[str, str]] = []  # (var_a, var_b) must differ

    def add_variable(self, name: str, domain: list[Any]) -> "ConstraintSolver":
        self._domains[name] = list(domain)
        return self

    def add_difference(self, var_a: str, var_b: str) -> "ConstraintSolver":
        self._constraints.append((var_a, var_b))
        return self

    def _is_consistent(self, assignment: dict[str, Any], var: str, value: Any) -> bool:
        for a, b in self._constraints:
            if var == a and b in assignment and assignment[b] == value:
                return False
            if var == b and a in assignment and assignment[a] == value:
                return False
        return True

    def _backtrack(self, assignment: dict[str, Any], variables: list[str]) -> dict[str, Any] | None:
        if not variables:
            return assignment
        # MRV: pick variable with the smallest domain.
        var = min(variables, key=lambda v: len(self._domains[v]))
        rest = [v for v in variables if v != var]
        for value in self._domains[var]:
            if self._is_consistent(assignment, var, value):
                next_assignment = dict(assignment)
                next_assignment[var] = value
                result = self._backtrack(next_assignment, rest)
                if result is not None:
                    return result
        return None

    def solve(self) -> dict[str, Any]:
        assignment = self._backtrack({}, list(self._domains))
        if assignment is None:
            return {"ok": False, "error": "no solution found", "solution": None}
        return {"ok": True, "solution": assignment}
