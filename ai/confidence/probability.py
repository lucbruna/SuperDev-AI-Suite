from __future__ import annotations

from typing import Any


class Probability:
    """Probability calculations for confidence system."""

    @staticmethod
    async def joint(probabilities: list[float]) -> float:
        if not probabilities:
            return 0.0
        result = 1.0
        for p in probabilities:
            result *= p
        return result

    @staticmethod
    async def conditional(p_a: float, p_b_given_a: float, p_b: float) -> float:
        if p_b == 0:
            return 0.0
        return (p_b_given_a * p_a) / p_b

    @staticmethod
    async def bayesian_fusion(priors: list[float], likelihoods: list[float]) -> float:
        if not priors or not likelihoods:
            return 0.5
        posterior = 0.5
        for prior, likelihood in zip(priors, likelihoods, strict=False):
            posterior = (likelihood * prior) / (likelihood * prior + (1 - likelihood) * (1 - prior) + 1e-10)
        return posterior

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        probabilities = context.get("probabilities", [])
        result = await self.joint(probabilities)
        return {"joint_probability": result}
