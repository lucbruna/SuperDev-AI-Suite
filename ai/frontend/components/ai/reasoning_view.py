"""
AI Reasoning View
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ReasoningStep(Enum):
    ANALYZE = "analyze"
    PLAN = "plan"
    EXECUTE = "execute"
    VERIFY = "verify"
    REFLECT = "reflect"


@dataclass
class Thought:
    step: ReasoningStep
    content: str
    confidence: float = 0.8
    alternatives: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ReasoningView:
    def __init__(self):
        self.thoughts: list[Thought] = []
        self.is_visible: bool = False

    def add_thought(self, thought: Thought) -> None:
        self.thoughts.append(thought)

    def clear(self) -> None:
        self.thoughts.clear()

    def toggle_visibility(self) -> None:
        self.is_visible = not self.is_visible

    def get_by_step(self, step: ReasoningStep) -> list[Thought]:
        return [t for t in self.thoughts if t.step == step]

    def render(self) -> dict[str, Any]:
        return {
            "thoughts": [{"step": t.step.value, "content": t.content, "confidence": t.confidence} for t in self.thoughts],
            "isVisible": self.is_visible,
        }
