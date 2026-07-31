from __future__ import annotations

import logging
from typing import Any


class ChainOfThought:
    """Builds step-by-step reasoning traces over a query and known facts."""

    def __init__(self, max_steps: int = 5) -> None:
        self._log = logging.getLogger("superdev.knowledge.reasoning.chain_of_thought")
        self.max_steps = max(1, max_steps)

    def reason(self, query: str, facts: list[str], conclusion: str = "") -> list[dict[str, Any]]:
        query_tokens = set(query.lower().split())
        scored = sorted(
            ((self._overlap(fact, query_tokens), fact) for fact in facts),
            key=lambda pair: pair[0],
            reverse=True,
        )
        steps: list[dict[str, Any]] = []
        for index, (score, fact) in enumerate(scored[: self.max_steps], start=1):
            steps.append(
                {
                    "step": index,
                    "input": query,
                    "fact": fact,
                    "relevance": round(score, 3),
                    "reasoning": f"used fact with relevance {score:.3f}",
                    "output": fact,
                }
            )
        if steps and conclusion:
            steps.append(
                {
                    "step": len(steps) + 1,
                    "input": "synthesis",
                    "fact": "",
                    "relevance": 1.0,
                    "reasoning": "combined relevant facts into a conclusion",
                    "output": conclusion,
                }
            )
        return steps

    def _overlap(self, fact: str, query_tokens: set[str]) -> float:
        if not query_tokens:
            return 0.0
        fact_tokens = set(fact.lower().split())
        return len(query_tokens & fact_tokens) / len(query_tokens)
