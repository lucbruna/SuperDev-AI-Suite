"""Optimization models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class OptimizationType(Enum):
    LINEAR = "linear"
    NONLINEAR = "nonlinear"
    INTEGER = "integer"
    CONSTRAINT = "constraint"
    MULTI_OBJECTIVE = "multi_objective"


class Objective(Enum):
    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"


class ConstraintType(Enum):
    EQUAL = "equal"
    LESS_EQUAL = "less_equal"
    GREATER_EQUAL = "greater_equal"
    RANGE = "range"


@dataclass
class Variable:
    name: str
    lower_bound: float = 0.0
    upper_bound: float = float("inf")
    var_type: str = "continuous"


@dataclass
class ObjectiveFunction:
    coefficients: dict[str, float] = field(default_factory=dict)
    constant: float = 0.0
    objective: Objective = Objective.MAXIMIZE


@dataclass
class Constraint:
    variable: str
    constraint_type: ConstraintType = ConstraintType.LESS_EQUAL
    value: float = 0.0
    coefficients: dict[str, float] = field(default_factory=dict)


@dataclass
class OptimizationProblem:
    problem_id: str
    name: str = ""
    variables: list[Variable] = field(default_factory=list)
    objective: ObjectiveFunction = field(default_factory=ObjectiveFunction)
    constraints: list[Constraint] = field(default_factory=list)
    opt_type: OptimizationType = OptimizationType.LINEAR


@dataclass
class Solution:
    problem_id: str
    values: dict[str, float] = field(default_factory=dict)
    objective_value: float = 0.0
    feasible: bool = True
    iterations: int = 0
    solved_at: datetime = field(default_factory=datetime.now)
    solver_name: str = ""
    solve_time_ms: float = 0.0
    error: str | None = None


@dataclass
class SensitivityResult:
    variable: str
    shadow_price: float = 0.0
    reduced_cost: float = 0.0
    allowable_increase: float = 0.0
    allowable_decrease: float = 0.0
