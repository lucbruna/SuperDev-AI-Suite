"""AIOS Reasoning Engine — unified entry to reasoning strategies.

Dispatches to logical, causal, probabilistic, symbolic and hybrid
reasoners based on strategy name or problem shape.
"""

from __future__ import annotations

from typing import Any

from .causal_reasoning import CausalReasoning
from .hybrid_reasoning import HybridReasoning
from .logical_reasoning import LogicalReasoning
from .probabilistic_reasoning import ProbabilisticReasoning
from .symbolic_reasoning import SymbolicReasoning

STRATEGIES = ("logical", "causal", "probabilistic", "symbolic", "hybrid")


class ReasoningEngine:
    """Compose multiple reasoners behind one API."""

    def __init__(self) -> None:
        self._reasoners = {
            "logical": LogicalReasoning(),
            "causal": CausalReasoning(),
            "probabilistic": ProbabilisticReasoning(),
            "symbolic": SymbolicReasoning(),
            "hybrid": HybridReasoning(),
        }

    def reason(self, strategy: str, premises: list[Any], **kwargs: Any) -> dict[str, Any]:
        reasoner = self._reasoners.get(strategy)
        if reasoner is None:
            return {"ok": False, "error": f"unknown strategy: {strategy}", "strategy": strategy}
        try:
            return reasoner.reason(premises, **kwargs)
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "strategy": strategy, "error": f"{type(exc).__name__}: {exc}"}

    def best_strategy(self, premises: list[Any]) -> str:
        """Pick a default strategy based on premise shape."""
        if any(isinstance(p, dict) and "cause" in p for p in premises):
            return "causal"
        if any(isinstance(p, dict) and "probability" in p for p in premises):
            return "probabilistic"
        return "logical"

    def strategies(self) -> list[str]:
        return list(STRATEGIES)
