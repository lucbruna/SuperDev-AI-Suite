"""AIOS Probabilistic Reasoning — belief estimation.

Works with premises carrying probabilities (dicts with "event" and
"probability") and computes basic belief updates and independence
estimates. Deterministic approximation, not a full Bayesian engine.
"""

from __future__ import annotations

from typing import Any


class ProbabilisticReasoning:
    """Probability-based reasoning over events."""

    def reason(self, premises: list[Any], **kwargs: Any) -> dict[str, Any]:
        events: dict[str, float] = {}
        for premise in premises:
            if isinstance(premise, dict) and "event" in premise and "probability" in premise:
                events[str(premise["event"])] = float(premise["probability"])
        query = kwargs.get("query")
        result: dict[str, Any] = {
            "ok": True,
            "strategy": "probabilistic",
            "beliefs": events,
        }
        if query is not None:
            result["query"] = query
            result["probability"] = events.get(str(query))
        if len(events) >= 2:
            # Independent co-occurrence estimate.
            p = 1.0
            for value in events.values():
                p *= value
            result["joint_independent"] = round(p, 4)
        return result
