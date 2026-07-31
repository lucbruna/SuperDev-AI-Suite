from __future__ import annotations

from typing import Any

from .neural_reasoning import NeuralReasoning
from .probabilistic_reasoning import ProbabilisticReasoning
from .symbolic_reasoning import SymbolicReasoning


class HybridReasoning:
    """Hybrid reasoning combining symbolic, probabilistic, and neural approaches."""

    def __init__(
        self,
        symbolic: SymbolicReasoning | None = None,
        probabilistic: ProbabilisticReasoning | None = None,
        neural: NeuralReasoning | None = None,
    ):
        self._symbolic = symbolic or SymbolicReasoning()
        self._probabilistic = probabilistic or ProbabilisticReasoning()
        self._neural = neural or NeuralReasoning()

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        symbolic_result = await self._symbolic.execute(context)
        probabilistic_result = await self._probabilistic.execute(context)
        neural_result = await self._neural.execute(context)
        combined = {
            "symbolic": symbolic_result,
            "probabilistic": probabilistic_result,
            "neural": neural_result,
            "ensemble_confidence": (
                symbolic_result.get("confidence", 0)
                + probabilistic_result.get("confidence", 0)
                + neural_result.get("confidence", 0)
            )
            / 3,
        }
        return combined
