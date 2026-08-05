"""Transition map — maps transitions between consecutive boards."""
from __future__ import annotations

from typing import Any


class TransitionMap:
    """Suggests transitions between consecutive boards."""

    TRANSITIONS = {
        ("intro", "opening"): "fade",
        ("opening", "presentation"): "cut",
        ("presentation", "explanation"): "wipe",
        ("explanation", "comparison"): "slide",
        ("comparison", "product"): "zoom",
        ("product", "testimonial"): "fade",
        ("testimonial", "closing"): "cut",
        ("closing", "credits"): "fade",
        ("credits", "outro"): "fade",
    }

    def between(self, prev: dict[str, Any], curr: dict[str, Any]) -> str:
        key = (prev.get("type", ""), curr.get("type", ""))
        return self.TRANSITIONS.get(key, "cut")

    def build(self, boards: list[dict[str, Any]]) -> list[dict[str, Any]]:
        transitions = []
        for i in range(1, len(boards)):
            transitions.append({"from": i - 1, "to": i, "type": self.between(boards[i - 1], boards[i])})
        return transitions


_transition_map: TransitionMap | None = None


def get_transition_map() -> TransitionMap:
    global _transition_map
    if _transition_map is None:
        _transition_map = TransitionMap()
    return _transition_map
