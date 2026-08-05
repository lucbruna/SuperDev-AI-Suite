"""Transition manager — apply transitions between adjacent clips."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError

VALID_TRANSITIONS = ("cut", "fade", "dissolve", "wipe", "slide", "zoom", "blur", "spin")


class TransitionManager:
    """Manages transitions applied at clip boundaries."""

    def __init__(self, engine: Any | None = None) -> None:
        if engine is None:
            from modules.ai_video_studio.ai_timeline.timeline_engine import get_timeline_engine

            engine = get_timeline_engine()
        self.engine = engine
        self._transitions: dict[str, dict[str, Any]] = {}

    def apply(
        self,
        transition_id: str,
        clip_a: str,
        clip_b: str,
        kind: str = "fade",
        duration: float = 0.5,
        **meta: Any,
    ) -> dict[str, Any]:
        if kind not in VALID_TRANSITIONS:
            raise ValidationError(
                f"Invalid transition '{kind}'. Use: {', '.join(VALID_TRANSITIONS)}",
                field="kind",
            )
        if duration < 0:
            raise ValidationError("Transition duration cannot be negative", field="duration")
        self._validate_clip(clip_a)
        self._validate_clip(clip_b)
        transition = {
            "id": transition_id,
            "clip_a": clip_a,
            "clip_b": clip_b,
            "kind": kind,
            "duration": duration,
            **meta,
        }
        self._transitions[transition_id] = transition
        return transition

    def get(self, transition_id: str) -> dict[str, Any] | None:
        return self._transitions.get(transition_id)

    def remove(self, transition_id: str) -> bool:
        return self._transitions.pop(transition_id, None) is not None

    def between(self, clip_a: str, clip_b: str) -> dict[str, Any] | None:
        for t in self._transitions.values():
            if {t["clip_a"], t["clip_b"]} == {clip_a, clip_b}:
                return t
        return None

    def list(self) -> list[dict[str, Any]]:
        return list(self._transitions.values())

    def count(self) -> int:
        return len(self._transitions)

    def _validate_clip(self, clip_id: str) -> None:
        if not any(c.get("id") == clip_id for c in self.engine.clips):
            raise ValidationError(f"Clip '{clip_id}' not found", field="clip_id")


_transition_manager: TransitionManager | None = None


def get_transition_manager() -> TransitionManager:
    global _transition_manager
    if _transition_manager is None:
        _transition_manager = TransitionManager()
    return _transition_manager
