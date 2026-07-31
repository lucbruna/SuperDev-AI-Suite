from __future__ import annotations

from typing import Any


class LLMEvaluator:
    """Evaluates LLM responses against criteria."""

    async def evaluate(
        self, prompt: str, response: dict[str, Any], criteria: list[str] | None = None
    ) -> dict[str, float]:
        criteria = criteria or ["relevance", "latency", "length"]
        scores: dict[str, float] = {}

        content = response.get("content", "")
        latency_ms = response.get("latency_ms", response.get("duration_ms", 0))
        expected = response.get("expected", prompt)

        if "relevance" in criteria:
            scores["relevance"] = self.calculate_relevance(content, expected)

        if "latency" in criteria:
            scores["latency"] = self.calculate_latency_score(latency_ms)

        if "length" in criteria:
            scores["length"] = self.calculate_length_score(content)

        return scores

    def calculate_relevance(self, response: str, expected: str) -> float:
        response_words = set(response.lower().split())
        expected_words = set(expected.lower().split())
        if not expected_words:
            return 0.0
        overlap = response_words & expected_words
        return len(overlap) / len(expected_words)

    def calculate_accuracy(self, expected: str, actual: str) -> float:
        if not expected:
            return 1.0
        expected_words = expected.split()
        actual_words = actual.split()
        matches = sum(1 for e, a in zip(expected_words, actual_words, strict=False) if e == a)
        return matches / max(len(expected_words), 1)

    def calculate_latency_score(self, latency_ms: float) -> float:
        if latency_ms <= 0:
            return 0.0
        if latency_ms < 500:
            return 1.0
        if latency_ms < 2000:
            return 0.8
        if latency_ms < 5000:
            return 0.5
        return 0.2

    def calculate_length_score(self, content: str) -> float:
        length = len(content)
        if length == 0:
            return 0.0
        if length < 50:
            return 0.3
        if length < 200:
            return 0.7
        if length < 1000:
            return 1.0
        return 0.8

    def to_dict(self) -> dict[str, Any]:
        return {
            "methods": ["evaluate", "calculate_relevance", "calculate_accuracy"],
        }
