from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class Conclusion:
    id: str
    conclusion: str
    confidence: float
    supporting_premises: list[str] = field(default_factory=list)
    contradicting_premises: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ConclusionEngine:
    def __init__(self) -> None:
        self._conclusions: dict[str, Conclusion] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True
        logger.info("ConclusionEngine initialized")

    async def stop(self) -> None:
        self._conclusions.clear()
        self._initialized = False
        logger.info("ConclusionEngine stopped")

    async def draw_conclusion(self, premises: list[str], hypothesis: dict[str, Any]) -> dict[str, Any]:
        if not premises:
            return {"conclusion": "insufficient_premises", "confidence": 0.0}

        hypothesis_text = hypothesis.get("hypothesis", "unknown")
        hypothesis_conf = hypothesis.get("confidence", 0.5)

        positive = sum(1 for p in premises if any(w in p.lower() for w in ["up", "high", "good", "growing", "strong", "positive"]))
        negative = sum(1 for p in premises if any(w in p.lower() for w in ["down", "low", "bad", "declining", "weak", "negative"]))
        total = len(premises)

        base_conf = 0.5
        if total > 0:
            base_conf = (positive / total) * 0.8 + 0.1 if positive > negative else (1 - negative / total) * 0.8 + 0.1

        confidence = (base_conf + hypothesis_conf) / 2

        if positive > negative:
            conclusion_text = f"favorable_outcome_based_on: {hypothesis_text}"
        elif negative > positive:
            conclusion_text = f"unfavorable_outcome_based_on: {hypothesis_text}"
        else:
            conclusion_text = f"neutral_outcome_based_on: {hypothesis_text}"

        conclusion_id = str(uuid.uuid4())
        conclusion = Conclusion(
            id=conclusion_id,
            conclusion=conclusion_text,
            confidence=min(confidence, 1.0),
            supporting_premises=[p for p in premises if any(w in p.lower() for w in ["up", "high", "good"])],
            contradicting_premises=[p for p in premises if any(w in p.lower() for w in ["down", "low", "bad"])],
        )
        self._conclusions[conclusion_id] = conclusion

        return {
            "id": conclusion_id,
            "conclusion": conclusion_text,
            "confidence": min(confidence, 1.0),
            "hypothesis_used": hypothesis_text,
        }

    async def evaluate_conclusion(self, conclusion_id: str) -> dict[str, Any]:
        conclusion = self._conclusions.get(conclusion_id)
        if not conclusion:
            return {"error": "conclusion_not_found", "valid": False}

        strength = len(conclusion.supporting_premises)
        weakness = len(conclusion.contradicting_premises)
        total = strength + weakness

        validity = 0.5
        if total > 0:
            validity = strength / total

        return {
            "id": conclusion_id,
            "valid": validity >= 0.5,
            "validity_score": validity,
            "strength": strength,
            "weakness": weakness,
        }

    async def compare_conclusions(self, conclusion_ids: list[str]) -> list[dict[str, Any]]:
        results = []
        for cid in conclusion_ids:
            conclusion = self._conclusions.get(cid)
            if conclusion:
                results.append({
                    "id": cid,
                    "conclusion": conclusion.conclusion,
                    "confidence": conclusion.confidence,
                })
        return sorted(results, key=lambda r: r["confidence"], reverse=True)

    async def get_conclusion_confidence(self, conclusion_id: str) -> float:
        conclusion = self._conclusions.get(conclusion_id)
        return conclusion.confidence if conclusion else 0.0

    async def summarize_findings(self, conclusion_ids: list[str]) -> dict[str, Any]:
        findings = []
        for cid in conclusion_ids:
            conclusion = self._conclusions.get(cid)
            if conclusion:
                findings.append({
                    "conclusion": conclusion.conclusion,
                    "confidence": conclusion.confidence,
                    "supporting": len(conclusion.supporting_premises),
                    "contradicting": len(conclusion.contradicting_premises),
                })

        if not findings:
            return {"summary": "no_findings", "overall_confidence": 0.0}

        avg_conf = sum(f["confidence"] for f in findings) / len(findings)
        total_supporting = sum(f["supporting"] for f in findings)
        total_contradicting = sum(f["contradicting"] for f in findings)

        return {
            "summary": f"analyzed_{len(findings)}_conclusions",
            "findings": findings,
            "overall_confidence": avg_conf,
            "total_supporting": total_supporting,
            "total_contradicting": total_contradicting,
        }
