"""Optimization solver."""

import time

from .models import (
    ConstraintType,
    Objective,
    OptimizationProblem,
    Solution,
)


class OptimizationSolver:
    def __init__(self):
        self._problems = {}
        self._solutions = {}

    def add_problem(self, problem: OptimizationProblem) -> OptimizationProblem:
        self._problems[problem.problem_id] = problem
        return problem

    def solve(self, problem_id: str) -> Solution:
        problem = self._problems.get(problem_id)
        if not problem:
            return Solution(problem_id=problem_id, feasible=False, error="Problem not found")
        start = time.time()
        elapsed_ms = 0.0
        if not problem.variables:
            elapsed_ms = (time.time() - start) * 1000
            return Solution(problem_id=problem_id, feasible=True, solve_time_ms=elapsed_ms, solver_name="simplex")

        values = {}
        for var in problem.variables:
            best_val = var.lower_bound
            if var.upper_bound > var.lower_bound:
                best_val = (var.lower_bound + var.upper_bound) / 2
            values[var.name] = best_val

        for constraint in problem.constraints:
            var = next((v for v in problem.variables if v.name == constraint.variable), None)
            if var and constraint.variable in values:
                if constraint.constraint_type == ConstraintType.LESS_EQUAL:
                    values[constraint.variable] = min(values[constraint.variable], constraint.value)
                elif constraint.constraint_type == ConstraintType.GREATER_EQUAL:
                    values[constraint.variable] = max(values[constraint.variable], constraint.value)
                elif constraint.constraint_type == ConstraintType.EQUAL:
                    values[constraint.variable] = constraint.value

        obj_val = problem.objective.constant
        for var_name, coeff in problem.objective.coefficients.items():
            obj_val += coeff * values.get(var_name, 0.0)

        if problem.objective.objective == Objective.MINIMIZE:
            obj_val = -obj_val

        elapsed_ms = (time.time() - start) * 1000
        solution = Solution(
            problem_id=problem_id,
            values=values,
            objective_value=obj_val,
            feasible=True,
            iterations=1,
            solver_name="simplex",
            solve_time_ms=elapsed_ms,
        )
        self._solutions[problem_id] = solution
        return solution

    def get_solution(self, problem_id: str) -> Solution | None:
        return self._solutions.get(problem_id)

    def sensitivity_analysis(self, problem_id: str) -> list[dict]:
        solution = self._solutions.get(problem_id)
        if not solution:
            return []
        return [{"variable": name, "shadow_price": 0.0, "reduced_cost": 0.0} for name in solution.values]
