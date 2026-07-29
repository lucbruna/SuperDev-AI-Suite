from __future__ import annotations

import asyncio
from typing import Any

WEIGHTS = {
    "source_quality": 0.35,
    "evidence": 0.30,
    "consistency": 0.25,
    "recency": 0.10,
}


class ConfidenceScorer:
    def __init__(self) -> None:
        self._breakdowns: dict[str, dict[str, Any]] = {}

    async def calculate_confidence(
        self, knowledge_id: str, content: str, source_score: float, fact_status: str
    ) -> float:
        await asyncio.sleep(0.01)
        evidence_score = await self.calculate_from_evidence(content)
        consistency_score = await self.calculate_from_consistency(content)
        source_quality_score = source_score

        confidence = (
            source_quality_score * WEIGHTS["source_quality"]
            + evidence_score * WEIGHTS["evidence"]
            + consistency_score * WEIGHTS["consistency"]
        )

        if fact_status == "verified":
            confidence = min(1.0, confidence + 0.1)
        elif fact_status == "contradicted":
            confidence = max(0.0, confidence - 0.3)

        confidence = round(max(0.0, min(1.0, confidence)), 4)

        self._breakdowns[knowledge_id] = {
            "source_quality": source_quality_score,
            "evidence": evidence_score,
            "consistency": consistency_score,
            "fact_status_penalty": 0.1 if fact_status == "verified" else (-0.3 if fact_status == "contradicted" else 0.0),
            "final_confidence": confidence,
            "weights_used": WEIGHTS,
        }
        return confidence

    async def calculate_from_evidence(self, content: str) -> float:
        await asyncio.sleep(0.01)
        length = len(content)
        if length == 0:
            return 0.0
        if length < 50:
            return 0.3
        if length < 200:
            return 0.5
        if length < 500:
            return 0.7
        return 0.9

    async def calculate_from_consistency(self, content: str) -> float:
        await asyncio.sleep(0.01)
        words = content.lower().split()
        if not words:
            return 0.0
        contradictions = {"however", "but", "although", "conversely", "nevertheless", "yet", "despite"}
        contradiction_count = sum(1 for w in words if w in contradictions)
        total = len(words)
        ratio = contradiction_count / total if total > 0 else 0
        score = max(0.0, 1.0 - ratio * 5)
        return round(score, 4)

    async def calculate_from_source_quality(self, source_score: float) -> float:
        await asyncio.sleep(0.01)
        return round(max(0.0, min(1.0, source_score)), 4)

    async def get_confidence_breakdown(self, knowledge_id: str) -> dict[str, Any]:
        return self._breakdowns.get(knowledge_id, {})