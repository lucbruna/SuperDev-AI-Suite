from __future__ import annotations

from typing import Any


class HallucinationDetector:
    """Detects hallucinated content in responses."""

    def __init__(self) -> None:
        self._known_facts: set[str] = set()

    def add_fact(self, fact: str) -> None:
        self._known_facts.add(fact.lower())

    async def detect(self, response: str, context: dict[str, Any]) -> dict[str, Any]:
        sentences = response.replace("!", ".").replace("?", ".").split(".")
        suspicious: list[str] = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            words = sentence.lower().split()
            if len(words) > 3:
                key = " ".join(words[:5])
                if not any(fact in sentence.lower() for fact in self._known_facts):
                    if self._known_facts:
                        suspicious.append(sentence[:80])
        return {
            "has_hallucination": len(suspicious) > 0,
            "suspicious_statements": suspicious,
            "total_sentences": len([s for s in sentences if s.strip()]),
        }
