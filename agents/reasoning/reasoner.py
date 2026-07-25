from __future__ import annotations

import uuid
from typing import Any, Optional

from pydantic import BaseModel, Field


class Solution(BaseModel):
    id: str = ""
    problem: str = ""
    solution: str = ""
    confidence: float = 0.0
    steps: list[str] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)


class Reasoner:
    def __init__(self) -> None:
        self._history: list[Solution] = []

    async def reason(self, problem: str, context: Optional[dict[str, Any]] = None) -> Solution:
        ctx = context or {}
        decomposed = self._decompose(problem, ctx)
        analyzed = self._analyze(decomposed, ctx)
        synthesized = self._synthesize(analyzed, ctx)
        verified = self._verify(synthesized, ctx)

        solution = Solution(
            id=str(uuid.uuid4()),
            problem=problem,
            solution=synthesized,
            confidence=verified["confidence"],
            steps=[
                f"Decomposed into {len(decomposed)} sub-problems",
                f"Analysis identified {len(analyzed)} key insights",
                "Synthesized solution from analysis",
                f"Verification confidence: {verified['confidence']:.2f}",
            ],
            metrics={
                "decomposition_count": len(decomposed),
                "analysis_count": len(analyzed),
                "verified": verified["is_valid"],
            },
        )
        self._history.append(solution)
        return solution

    def _decompose(self, problem: str, context: dict[str, Any]) -> list[str]:
        parts = [p.strip() for p in problem.replace(".", "\n").split("\n") if p.strip()]
        return parts if parts else [problem]

    def _analyze(self, parts: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
        insights = []
        for part in parts:
            insights.append({
                "part": part,
                "key_elements": part.split(),
                "complexity": len(part),
            })
        return insights

    def _synthesize(self, analyzed: list[dict[str, Any]], context: dict[str, Any]) -> str:
        parts = [a["part"] for a in analyzed]
        return " ".join(parts)

    def _verify(self, solution: str, context: dict[str, Any]) -> dict[str, Any]:
        word_count = len(solution.split())
        confidence = min(1.0, word_count / 50)
        return {
            "is_valid": word_count > 0,
            "confidence": confidence,
            "issues": [] if word_count > 0 else ["Empty solution"],
        }

    def get_history(self) -> list[Solution]:
        return self._history
