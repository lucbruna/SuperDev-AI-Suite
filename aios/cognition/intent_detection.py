"""AIOS Intent Detection — classify the goal behind raw input.

Rule/keyword-based intent classification over registered intent
patterns; deterministic and extensible.
"""

from __future__ import annotations

from typing import Any

DEFAULT_INTENTS: dict[str, list[str]] = {
    "create": ["create", "generate", "make", "build", "write"],
    "analyze": ["analyze", "review", "inspect", "audit", "check"],
    "publish": ["publish", "share", "post", "deploy", "release"],
    "optimize": ["optimize", "improve", "speed up", "enhance", "boost"],
    "schedule": ["schedule", "plan", "book", "remind"],
    "answer": ["what", "why", "how", "explain", "tell"],
}


class IntentDetection:
    """Detect intent by keyword matching against registered patterns."""

    def __init__(self, intents: dict[str, list[str]] | None = None) -> None:
        self._intents = dict(DEFAULT_INTENTS)
        if intents:
            self._intents.update(intents)

    def register(self, intent: str, keywords: list[str]) -> "IntentDetection":
        self._intents[intent] = keywords
        return self

    def detect(self, raw: Any) -> dict[str, Any]:
        text = str(raw).lower()
        scored: list[tuple[int, str]] = []
        for intent, keywords in self._intents.items():
            score = sum(1 for kw in keywords if kw in text)
            if score:
                scored.append((score, intent))
        if not scored:
            return {"intent": "unknown", "confidence": 0.0, "matches": []}
        scored.sort(key=lambda pair: -pair[0])
        top_score, top_intent = scored[0]
        return {
            "intent": top_intent,
            "confidence": round(top_score / max(len(self._intents[top_intent]), 1), 3),
            "matches": [intent for _, intent in scored],
        }
