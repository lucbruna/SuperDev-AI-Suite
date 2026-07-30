from __future__ import annotations

from typing import Any


class SemanticValidator:
    """Validates semantic coherence and meaning."""

    def __init__(self) -> None:
        self._expected_topics: list[str] = []

    def add_topic(self, topic: str) -> None:
        self._expected_topics.append(topic.lower())

    async def validate(self, response: str, context: dict[str, Any]) -> dict[str, Any]:
        missing: list[str] = []
        for topic in self._expected_topics:
            if topic not in response.lower():
                missing.append(topic)
        key_terms = context.get("key_terms", [])
        term_missing = [t for t in key_terms if t.lower() not in response.lower()]
        return {
            "valid": len(missing) == 0,
            "missing_topics": missing,
            "missing_terms": term_missing,
        }
