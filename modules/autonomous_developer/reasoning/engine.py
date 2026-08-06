"""Reasoning engine — deterministic goal decomposition and option scoring.

LLM-free structured reasoning: a goal is decomposed into steps, candidate
options are scored against keyword criteria, and the best option is selected
with a traceable rationale.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from modules.autonomous_developer.core.exceptions import GenerationError


@dataclass(slots=True)
class ReasoningResult:
    """Outcome of one reasoning pass."""

    goal: str = ""
    steps: list[str] = field(default_factory=list)
    scores: list[dict[str, Any]] = field(default_factory=list)
    selected: str = ""
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal": self.goal,
            "steps": list(self.steps),
            "scores": list(self.scores),
            "selected": self.selected,
            "rationale": self.rationale,
        }


def decompose(goal: str) -> list[str]:
    """Split a goal into ordered steps on newlines and sentence boundaries."""
    if not goal or not goal.strip():
        return []
    chunks = []
    for raw in goal.replace("\r", "\n").split("\n"):
        for part in raw.split(". "):
            cleaned = part.strip(" .")
            if cleaned:
                chunks.append(cleaned)
    return chunks or [goal.strip()]


def score_options(
    options: list[str], criteria: dict[str, float]
) -> list[dict[str, Any]]:
    """Score each option by keyword presence, sorted best first (stable)."""
    scored: list[dict[str, Any]] = []
    for index, option in enumerate(options):
        lowered = option.lower()
        matched = [
            criterion
            for criterion in criteria
            if criterion.lower() in lowered
        ]
        total = sum(criteria[criterion] for criterion in matched)
        scored.append(
            {"option": option, "score": round(total, 3), "matched": matched, "index": index}
        )
    scored.sort(key=lambda entry: (-entry["score"], entry["index"]))
    for entry in scored:
        entry.pop("index", None)
    return scored


class ReasoningEngine:
    """Deterministic structured reasoning over goals and options."""

    def reason(
        self,
        goal: str,
        options: list[str] | None = None,
        criteria: dict[str, float] | None = None,
    ) -> ReasoningResult:
        """Decompose ``goal`` and, when options are given, score and select."""
        steps = decompose(goal)
        scores = score_options(options or [], criteria or {})
        selected = scores[0]["option"] if scores else ""
        if selected:
            rationale = (
                f"Selected '{selected}' with score {scores[0]['score']} "
                f"from {len(scores)} option(s)."
            )
        else:
            rationale = "No options were provided to choose from."
        return ReasoningResult(
            goal=goal,
            steps=steps,
            scores=scores,
            selected=selected,
            rationale=rationale,
        )

    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs: Any) -> ReasoningResult:
        """Runtime component entry point (``goal`` required)."""
        if not goal or not goal.strip():
            raise GenerationError("A goal is required for reasoning")
        result = self.reason(
            goal,
            options=kwargs.get("options"),
            criteria=kwargs.get("criteria"),
        )
        ctx.record("reasoning_steps", len(result.steps))
        ctx.record("reasoning_options", len(result.scores))
        ctx.record("reasoning_selected", result.selected)
        ctx.publish(
            "reasoning.completed",
            {
                "steps": len(result.steps),
                "options": len(result.scores),
                "selected": result.selected,
            },
        )
        return result
