from __future__ import annotations

from typing import Any


class ProbabilisticReasoning:
    """Probabilistic reasoning with Bayesian inference."""

    def __init__(self) -> None:
        self._priors: dict[str, float] = {}

    def set_prior(self, event: str, probability: float) -> None:
        self._priors[event] = probability

    async def bayesian_update(self, prior: float, likelihood: float, evidence: float) -> float:
        if evidence == 0:
            return prior
        return (likelihood * prior) / evidence

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        hypotheses = context.get("hypotheses", [])
        evidence = context.get("evidence", {})
        results: list[dict[str, Any]] = []
        for h in hypotheses:
            prior = self._priors.get(h, 0.5)
            likelihood = evidence.get(h, {}).get("likelihood", 0.5)
            posterior = await self.bayesian_update(prior, likelihood, 1.0)
            results.append({"hypothesis": h, "posterior": posterior})
        confidence = max((r["posterior"] for r in results), default=0.0) if results else 0.0
        return {"results": results, "confidence": confidence}
