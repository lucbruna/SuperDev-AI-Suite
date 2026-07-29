from __future__ import annotations

import logging
import random
import uuid
from typing import Any, Optional

logger = logging.getLogger(__name__)


class HypothesisBuilder:
    def __init__(self) -> None:
        self._hypotheses: dict[str, dict[str, Any]] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True
        logger.info("HypothesisBuilder initialized")

    async def stop(self) -> None:
        self._hypotheses.clear()
        self._initialized = False
        logger.info("HypothesisBuilder stopped")

    async def build_hypothesis(self, premises: list[str]) -> dict[str, Any]:
        if not premises:
            return {"hypothesis": "no_premises", "confidence": 0.0}

        combined = " ".join(premises).lower()
        words = [w for w in combined.split() if len(w) > 3]
        key_words = list(set(words))[:5]

        hypothesis_text = f"hypothesis: {', '.join(key_words)} indicates a relationship"
        hypothesis_id = str(uuid.uuid4())

        hypothesis = {
            "id": hypothesis_id,
            "hypothesis": hypothesis_text,
            "premises": premises,
            "confidence": min(0.5 + len(premises) * 0.1, 0.95),
            "status": "proposed",
        }

        self._hypotheses[hypothesis_id] = hypothesis
        return hypothesis

    async def generate_alternatives(self, hypothesis: dict[str, Any], count: int = 3) -> list[dict[str, Any]]:
        premises = hypothesis.get("premises", [])
        alternatives = []

        for i in range(count):
            alt_words = []
            for p in premises:
                shuffled = p.split()
                random.shuffle(shuffled)
                alt_words.append(" ".join(shuffled))

            alt = {
                "id": str(uuid.uuid4()),
                "hypothesis": f"alternative_{i}: {'; '.join(alt_words)}",
                "premises": premises,
                "confidence": max(0.1, hypothesis.get("confidence", 0.5) - i * 0.15),
                "status": "alternative",
                "parent_id": hypothesis.get("id"),
            }
            alternatives.append(alt)
            self._hypotheses[alt["id"]] = alt

        return alternatives

    async def rank_hypotheses(self, hypotheses: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(hypotheses, key=lambda h: h.get("confidence", 0.0), reverse=True)

    async def get_supporting_evidence(self, hypothesis: dict[str, Any]) -> list[str]:
        premises = hypothesis.get("premises", [])
        evidence = []
        for p in premises:
            if random.random() > 0.3:
                evidence.append(f"evidence_supports: {p}")
        return evidence

    async def get_contradicting_evidence(self, hypothesis: dict[str, Any]) -> list[str]:
        premises = hypothesis.get("premises", [])
        evidence = []
        for p in premises:
            if random.random() > 0.7:
                evidence.append(f"evidence_contradicts: {p}")
        return evidence

    def get_hypothesis(self, hypothesis_id: str) -> Optional[dict[str, Any]]:
        return self._hypotheses.get(hypothesis_id)
