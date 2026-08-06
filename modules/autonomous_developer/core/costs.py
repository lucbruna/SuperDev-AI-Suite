"""Token usage and cost accounting for the autonomous flow.

Conservatively model-agnostic USD rates (per 1k tokens) shared by the
evaluation harness, the runtime status and any tracing consumer.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = ["CostTracker", "estimate_cost"]

# USD per 1k tokens — conservative defaults, no per-provider model needed.
PRICE_INPUT_PER_1K = 0.00015
PRICE_OUTPUT_PER_1K = 0.00060


def estimate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    """USD estimate from token counts."""
    return (
        prompt_tokens * PRICE_INPUT_PER_1K + completion_tokens * PRICE_OUTPUT_PER_1K
    ) / 1000.0


@dataclass(slots=True)
class CostTracker:
    """Accumulates per-phase LLM usage and rolls it up into totals."""

    entries: list[dict[str, Any]] = field(default_factory=list)

    def record(self, phase: str, prompt_tokens: int, completion_tokens: int) -> dict[str, Any]:
        entry = {
            "phase": phase,
            "prompt_tokens": int(prompt_tokens),
            "completion_tokens": int(completion_tokens),
            "cost_usd": estimate_cost(int(prompt_tokens), int(completion_tokens)),
        }
        self.entries.append(entry)
        return entry

    def totals(self) -> dict[str, Any]:
        return {
            "calls": len(self.entries),
            "prompt_tokens": sum(e["prompt_tokens"] for e in self.entries),
            "completion_tokens": sum(e["completion_tokens"] for e in self.entries),
            "cost_usd": round(sum(e["cost_usd"] for e in self.entries), 6),
        }

    def reset(self) -> None:
        self.entries.clear()
