"""Constraint solver."""
from __future__ import annotations

from typing import Any


class ConstraintSolver:
    def __init__(self) -> None:
        self._constraints: list[dict[str, Any]] = []
        self._solutions: list[dict[str, Any]] = []
    def add_constraint(self, name: str, constraint_type: str, parameters: dict[str, Any]) -> dict[str, Any]:
        constraint = {"name": name, "type": constraint_type, "parameters": parameters}
        self._constraints.append(constraint)
        return constraint
    def solve(self, variables: dict[str, Any], objective: str = "satisfy") -> dict[str, Any]:
        feasible = True
        violations = []
        for c in self._constraints:
            if c["type"] == "range":
                var_name = c["parameters"].get("variable", "")
                min_val = c["parameters"].get("min", 0)
                max_val = c["parameters"].get("max", 100)
                val = variables.get(var_name, 0)
                if val < min_val or val > max_val:
                    feasible = False
                    violations.append({"constraint": c["name"], "variable": var_name, "value": val})
            elif c["type"] == "equality":
                var_name = c["parameters"].get("variable", "")
                expected = c["parameters"].get("value", 0)
                if variables.get(var_name, 0) != expected:
                    feasible = False
                    violations.append({"constraint": c["name"], "variable": var_name})
        solution = {"variables": variables, "feasible": feasible, "violations": violations}
        self._solutions.append(solution)
        return solution
    def get_solutions(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._solutions[-limit:]
    def list_constraints(self) -> list[dict[str, Any]]:
        return self._constraints
    def clear_constraints(self) -> int:
        n = len(self._constraints)
        self._constraints.clear()
        return n
    def count(self) -> int:
        return len(self._constraints)
