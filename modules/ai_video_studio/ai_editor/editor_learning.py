"""Editor learning — learns editing preferences from observed sessions.

Tracks transitions used, clip durations and common effect choices, then
recommends sensible defaults for new edits (e.g. the most-used transition
between two clips of similar length).
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.learning")


class EditorLearning:
    def __init__(self) -> None:
        self._transitions: Counter[str] = Counter()
        self._durations: list[float] = []
        self._effects: Counter[str] = Counter()
        self._session_ops: Counter[str] = Counter()

    def observe_edit(self, op: str, **meta: Any) -> None:
        self._session_ops[op] += 1
        if op == "transition" and meta.get("name"):
            self._transitions[meta["name"]] += 1
        if op == "effect" and meta.get("name"):
            self._effects[meta["name"]] += 1
        if meta.get("duration"):
            self._durations.append(float(meta["duration"]))

    def recommend_transition(self, clip_duration: float) -> str:
        """Most-used transition, defaulting by clip length (short clips → cut)."""
        if clip_duration < 2.0:
            return "cut"
        if self._transitions:
            return self._transitions.most_common(1)[0][0]
        return "dissolve" if clip_duration < 8.0 else "fade_black"

    def recommend_effect(self) -> str | None:
        if not self._effects:
            return None
        return self._effects.most_common(1)[0][0]

    def avg_duration(self) -> float:
        if not self._durations:
            return 0.0
        return sum(self._durations) / len(self._durations)

    def summary(self) -> dict[str, Any]:
        return {
            "transitions": dict(self._transitions),
            "effects": dict(self._effects),
            "operations": dict(self._session_ops),
            "avg_duration": self.avg_duration(),
            "sessions_recorded": len(self._session_ops),
        }

    def reset(self) -> None:
        self._transitions.clear()
        self._durations.clear()
        self._effects.clear()
        self._session_ops.clear()
