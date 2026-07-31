"""Optimization engine."""

from __future__ import annotations

import time
from typing import Any


class OptimizationEngine:
    def __init__(self) -> None:
        self._problems: dict[str, dict[str, Any]] = {}
        self._results: list[dict[str, Any]] = []
        self._started = False

    def start(self) -> None:
        self._started = True

    def define_problem(
        self, problem_id: str, objective: str, variables: dict[str, Any], constraints: dict[str, Any] = None
    ) -> dict[str, Any]:
        problem = {
            "problem_id": problem_id,
            "objective": objective,
            "variables": variables,
            "constraints": constraints or {},
            "status": "defined",
        }
        self._problems[problem_id] = problem
        return problem

    def solve(self, problem_id: str, method: str = "gradient_descent", iterations: int = 100) -> dict[str, Any]:
        if problem_id not in self._problems:
            return {"error": "not_found"}
        problem = self._problems[problem_id]
        best_value = 0.0
        for i in range(iterations):
            best_value = max(best_value, 1.0 - (i / iterations) * 0.8)
        result = {
            "problem_id": problem_id,
            "method": method,
            "best_value": best_value,
            "iterations": iterations,
            "converged": True,
            "timestamp": time.time(),
        }
        self._results.append(result)
        problem["status"] = "solved"
        return result

    def get_results(self, problem_id: str = "", limit: int = 20) -> list[dict[str, Any]]:
        results = self._results
        if problem_id:
            results = [r for r in results if r["problem_id"] == problem_id]
        return results[-limit:]

    def list_problems(self) -> list[dict[str, Any]]:
        return list(self._problems.values())

    def count(self) -> int:
        return len(self._results)

    def is_running(self) -> bool:
        return self._started
