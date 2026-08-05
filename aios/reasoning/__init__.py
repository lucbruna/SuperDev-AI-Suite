"""AIOS Reasoning — inference subsystem.

Exposes the reasoning engine and its strategies: logical, causal,
probabilistic, symbolic and hybrid, plus the forward-chaining rule
engine and a backtracking constraint solver.
"""

from __future__ import annotations

from .causal_reasoning import CausalReasoning
from .constraint_solver import ConstraintSolver
from .hybrid_reasoning import HybridReasoning
from .logical_reasoning import LogicalReasoning
from .probabilistic_reasoning import ProbabilisticReasoning
from .reasoning_engine import STRATEGIES, ReasoningEngine
from .rule_engine import RuleEngine
from .symbolic_reasoning import SymbolicReasoning

__all__ = [
    "ReasoningEngine",
    "LogicalReasoning",
    "CausalReasoning",
    "ProbabilisticReasoning",
    "SymbolicReasoning",
    "HybridReasoning",
    "RuleEngine",
    "ConstraintSolver",
    "STRATEGIES",
]
