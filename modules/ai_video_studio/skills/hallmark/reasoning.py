"""Hallmark reasoning — deterministic step-by-step reasoning chain."""
from __future__ import annotations
from typing import Any


class ReasoningChain:
    """Build a reasoning trace: premise → evidence → inference → conclusion."""

    def __init__(self) -> None:
        pass

    def chain(self, premise: str, *facts: str) -> list[dict[str, str]]:
        """Return an ordered reasoning trace for a premise and supporting facts."""
        facts = facts or (premise,)
        steps: list[dict[str, str]] = [
            {"step": "premise", "content": premise},
        ]
        for index, fact in enumerate(facts, start=1):
            steps.append({"step": f"evidence-{index}", "content": fact})
        steps.append(
            {"step": "inference", "content": f"Given the above, {premise} is supported."}
        )
        steps.append(
            {"step": "conclusion", "content": f"Act on {premise} with the gathered evidence."}
        )
        return steps
