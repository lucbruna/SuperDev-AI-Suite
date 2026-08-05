"""AIOS Cognition Engine — orchestrated perception pipeline.

Composes perception, attention, intent, context and decision modules
into a single ``cognize`` pass producing a structured cognition result.
"""

from __future__ import annotations

import time
from typing import Any

from .attention import Attention
from .context_builder import ContextBuilder
from .decision_support import DecisionSupport
from .intent_detection import IntentDetection
from .perception import Perception


class CognitionEngine:
    """Pipeline that turns raw input into a decision-ready cognition."""

    def __init__(self) -> None:
        self.perception = Perception()
        self.attention = Attention()
        self.intent = IntentDetection()
        self.context = ContextBuilder()
        self.decision = DecisionSupport()

    def cognize(self, raw_input: Any, focus: list[str] | None = None) -> dict[str, Any]:
        started = time.perf_counter()
        percepts = self.perception.interpret(raw_input)
        selected = self.attention.filter(percepts, focus=focus)
        intent = self.intent.detect(raw_input)
        built = self.context.build(raw_input=raw_input, percepts=selected, intent=intent)
        return {
            "ok": True,
            "percepts": percepts,
            "selected": selected,
            "intent": intent,
            "context": built,
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
        }

    def decide(self, options: list[dict[str, Any]], criteria: dict[str, float]) -> dict[str, Any]:
        return self.decision.recommend(options, criteria)

    def snapshot(self) -> dict[str, Any]:
        return {
            "modules": [
                "perception",
                "attention",
                "intent",
                "context",
                "decision",
            ]
        }
