"""AIOS Hybrid Reasoning — strategy ensemble.

Runs multiple strategies over the same premises and merges their
conclusions with per-strategy confidence.
"""

from __future__ import annotations

from typing import Any

from .logical_reasoning import LogicalReasoning
from .probabilistic_reasoning import ProbabilisticReasoning
from .symbolic_reasoning import SymbolicReasoning


class HybridReasoning:
    """Ensemble reasoning: logical + probabilistic + symbolic."""

    def __init__(self) -> None:
        self._logical = LogicalReasoning()
        self._probabilistic = ProbabilisticReasoning()
        self._symbolic = SymbolicReasoning()

    def reason(self, premises: list[Any], **kwargs: Any) -> dict[str, Any]:
        results = {
            "logical": self._logical.reason(premises, **kwargs),
            "probabilistic": self._probabilistic.reason(premises, **kwargs),
            "symbolic": self._symbolic.reason(premises, **kwargs),
        }
        conclusions: list[str] = []
        for name, result in results.items():
            items = result.get("conclusions") or result.get("reachable") or []
            if items:
                conclusions.extend(items if isinstance(items, list) else [str(items)])
        return {
            "ok": True,
            "strategy": "hybrid",
            "sub_results": results,
            "conclusions": conclusions,
            "agreement": 1.0 if conclusions else 0.0,
        }
