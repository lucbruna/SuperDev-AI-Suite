"""Safety score evaluation."""
from __future__ import annotations

from typing import Any


class SafetyEvaluator:
    def __init__(self) -> None:
        self._results: list[dict[str, Any]] = []
        self._blocked_patterns: list[str] = ["hack", "exploit", "malware", "phishing"]
    def evaluate(self, response: str) -> dict[str, Any]:
        risks = []
        for pattern in self._blocked_patterns:
            if pattern.lower() in response.lower():
                risks.append(pattern)
        score = 1.0 - (len(risks) * 0.2)
        score = max(0, score)
        result = {"score": score, "risks": risks, "safe": len(risks) == 0}
        self._results.append(result)
        return result
    def check_injection(self, prompt: str) -> dict[str, Any]:
        injection_patterns = ["ignore previous", "ignore all", "system prompt", "jailbreak"]
        detected = [p for p in injection_patterns if p.lower() in prompt.lower()]
        return {"detected": len(detected) > 0, "patterns": detected}
    def get_history(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._results[-limit:]
    def safety_rate(self) -> float:
        if not self._results:
            return 1.0
        safe = sum(1 for r in self._results if r["safe"])
        return safe / len(self._results)
    def count(self) -> int:
        return len(self._results)
    def add_blocked_pattern(self, pattern: str) -> None:
        self._blocked_patterns.append(pattern)
