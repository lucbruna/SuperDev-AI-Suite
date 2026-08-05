"""AIOS Causal Reasoning — cause-effect inference.

Models premises as cause -> effect links and answers queries about
chains of causality and likely effects of interventions.
"""

from __future__ import annotations

from typing import Any


class CausalReasoning:
    """Inference over cause-effect links."""

    def __init__(self) -> None:
        self._links: list[tuple[str, str, float]] = []  # (cause, effect, strength)

    def learn(self, cause: str, effect: str, strength: float = 1.0) -> "CausalReasoning":
        self._links.append((cause, effect, float(strength)))
        return self

    def reason(self, premises: list[Any], **kwargs: Any) -> dict[str, Any]:
        for premise in premises:
            if isinstance(premise, dict) and "cause" in premise and "effect" in premise:
                self.learn(str(premise["cause"]), str(premise["effect"]), premise.get("strength", 1.0))
        query = kwargs.get("query")
        if query is None:
            return {
                "ok": True,
                "strategy": "causal",
                "links": [{"cause": c, "effect": e, "strength": s} for c, e, s in self._links],
                "chain": [],
            }
        chain: list[str] = []
        current = str(query)
        visited: set[str] = set()
        while current not in visited:
            visited.add(current)
            chain.append(current)
            nxt = next((e for c, e, _s in self._links if c == current), None)
            if nxt is None:
                break
            current = nxt
        return {
            "ok": True,
            "strategy": "causal",
            "links": [{"cause": c, "effect": e, "strength": s} for c, e, s in self._links],
            "query": query,
            "chain": chain,
        }
