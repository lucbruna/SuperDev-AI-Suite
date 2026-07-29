from __future__ import annotations

import asyncio
import hashlib
from typing import Any

PREDEFINED_FACTS: dict[str, dict[str, Any]] = {
    "earth_round": {
        "claim": "The Earth is round",
        "is_true": True,
        "category": "science",
        "source": "scientific_consensus",
    },
    "sun_orbits_earth": {
        "claim": "The Sun orbits the Earth",
        "is_true": False,
        "category": "science",
        "source": "geocentric_model",
    },
    "water_boils_at_100c": {
        "claim": "Water boils at 100 degrees Celsius at sea level",
        "is_true": True,
        "category": "science",
        "source": "physics",
    },
    "python_is_compiled": {
        "claim": "Python is a compiled language",
        "is_true": False,
        "category": "programming",
        "source": "language_design",
    },
}


class FactChecker:
    def __init__(self) -> None:
        self._facts = dict(PREDEFINED_FACTS)
        self._check_history: list[dict[str, Any]] = []

    async def check_fact(self, knowledge_id: str, content: str) -> dict[str, Any]:
        await asyncio.sleep(0.01)
        claim = content.strip().lower()
        for fact_id, fact in self._facts.items():
            if fact["claim"].lower() in claim:
                result = {
                    "knowledge_id": knowledge_id,
                    "fact_id": fact_id,
                    "matched_claim": fact["claim"],
                    "is_true": fact["is_true"],
                    "status": "verified" if fact["is_true"] else "contradicted",
                    "source": fact["source"],
                }
                self._check_history.append(result)
                return result

        result = {
            "knowledge_id": knowledge_id,
            "fact_id": None,
            "matched_claim": None,
            "is_true": None,
            "status": "unverified",
            "source": None,
        }
        self._check_history.append(result)
        return result

    async def verify_claim(self, claim: str) -> dict[str, Any]:
        await asyncio.sleep(0.01)
        claim_lower = claim.lower()
        for fact_id, fact in self._facts.items():
            if fact["claim"].lower() == claim_lower:
                return {
                    "claim": claim,
                    "is_true": fact["is_true"],
                    "status": "verified" if fact["is_true"] else "contradicted",
                    "fact_id": fact_id,
                    "source": fact["source"],
                }
        return {
            "claim": claim,
            "is_true": None,
            "status": "unverified",
            "fact_id": None,
            "source": None,
        }

    async def find_supporting_evidence(self, content: str) -> list[dict[str, Any]]:
        await asyncio.sleep(0.01)
        evidence: list[dict[str, Any]] = []
        content_lower = content.lower()
        for fact_id, fact in self._facts.items():
            if fact["is_true"] and fact["claim"].lower() in content_lower:
                evidence.append({
                    "fact_id": fact_id,
                    "claim": fact["claim"],
                    "type": "supporting",
                    "source": fact["source"],
                })
        return evidence

    async def find_contradicting_evidence(self, content: str) -> list[dict[str, Any]]:
        await asyncio.sleep(0.01)
        evidence: list[dict[str, Any]] = []
        content_lower = content.lower()
        for fact_id, fact in self._facts.items():
            if not fact["is_true"] and fact["claim"].lower() in content_lower:
                evidence.append({
                    "fact_id": fact_id,
                    "claim": fact["claim"],
                    "type": "contradicting",
                    "source": fact["source"],
                })
        return evidence

    async def get_verification_status(self, knowledge_id: str) -> dict[str, Any]:
        await asyncio.sleep(0.01)
        for entry in reversed(self._check_history):
            if entry["knowledge_id"] == knowledge_id:
                return entry
        return {
            "knowledge_id": knowledge_id,
            "status": "not_checked",
        }