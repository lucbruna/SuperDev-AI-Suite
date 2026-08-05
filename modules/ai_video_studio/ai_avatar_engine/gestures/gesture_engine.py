"""Gesture engine — aggregates gesture libraries and plans timelines."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_avatar_engine.gestures.idle_pose import Gesture

# context → gesture library module
_CONTEXT_MODULES = {
    "presentation": "presentation_gestures",
    "teaching": "teaching_gestures",
    "interview": "interview_gestures",
    "conversation": "conversation_gestures",
    "idle": "idle_pose",
    "applause": "applause",
    "pointing": "pointing",
    "waving": "waving",
    "hands": "hand_movements",
    "arms": "arm_movements",
    "shoulders": "shoulder_movements",
    "head": "head_movements",
}

_BASE_GESTURES: list[Gesture] = [
    Gesture("neutral", 0.0, 0.0, 0.0, "neutral"),
    Gesture("point", 0.85, 0.3, 0.15, "tilt"),
    Gesture("wave", 0.85, 0.2, 0.0, "neutral"),
    Gesture("nod", 0.2, 0.2, 0.0, "nod"),
    Gesture("shake", 0.2, 0.2, 0.0, "shake"),
    Gesture("thumbs_up", 0.9, 0.1, -0.1, "tilt"),
    Gesture("cross_arms", 0.35, 0.35, 0.05, "neutral"),
    Gesture("hands_open", 0.5, 0.5, 0.0, "neutral"),
    Gesture("shrug", 0.5, 0.5, -0.2, "neutral"),
]

_TRIGGERS = {
    "important": "point", "key": "point", "note": "point", "look": "point",
    "hello": "wave", "welcome": "wave", "goodbye": "wave",
    "agree": "nod", "yes": "nod", "correct": "nod",
    "no": "shake", "wrong": "shake", "never": "shake",
    "great": "thumbs_up", "awesome": "thumbs_up", "amazing": "thumbs_up",
    "maybe": "shrug", "perhaps": "shrug",
    "imagine": "hands_open", "picture": "hands_open",
}


class GestureEngine:
    """Plans per-frame gesture timelines from scripts and contexts."""

    def names(self) -> list[str]:
        return [g.name for g in _BASE_GESTURES]

    def get(self, name: str) -> Gesture:
        for gesture in self.all():
            if gesture.name == name:
                return gesture
        raise KeyError(f"unknown gesture '{name}'")

    def all(self) -> list[Gesture]:
        """All gestures: base vocabulary + every context library."""
        gestures = list(_BASE_GESTURES)
        for module_name in _CONTEXT_MODULES.values():
            module = __import__(f"{__name__.rsplit('.', 1)[0]}.{module_name}",
                                fromlist=["gestures"])
            for gesture in module.gestures():
                if not any(g.name == gesture.name for g in gestures):
                    gestures.append(gesture)
        return gestures

    def for_context(self, context: str) -> list[Gesture]:
        module_name = _CONTEXT_MODULES.get(context)
        if module_name is None:
            return list(_BASE_GESTURES)
        module = __import__(f"{__name__.rsplit('.', 1)[0]}.{module_name}",
                            fromlist=["gestures"])
        return list(module.gestures())

    def plan_for_text(self, text: str, *, duration: float,
                      fps: int = 24) -> list[dict[str, Any]]:
        """Per-frame gesture timeline driven by script keywords."""
        import math
        import re

        frame_count = max(1, int(duration * fps))
        sentences = re.split(r"(?<=[.!?])\s+", text.strip()) or [text]
        sentence_count = max(len(sentences), 1)
        frames: list[dict[str, Any]] = []
        for f in range(frame_count):
            t = f / fps
            norm = t / max(duration, 1e-6)
            sentence = sentences[min(int(norm * sentence_count), sentence_count - 1)].lower()
            gesture = self._gesture_for_sentence(sentence)
            base = self.get(gesture)
            amp = 0.75 + 0.25 * abs(math.sin(f / fps * 1.7))
            frames.append({
                "frame": f, "time": round(t, 3), "gesture": gesture,
                "arm_left": round(base.arm_left * amp, 3),
                "arm_right": round(base.arm_right * amp, 3),
                "lean": round(base.lean * amp, 3),
                "head": base.head,
            })
        return frames

    @staticmethod
    def _gesture_for_sentence(sentence: str) -> str:
        for word, gesture in _TRIGGERS.items():
            if word in sentence:
                return gesture
        if sentence.endswith("!") or sentence.endswith("?"):
            return "point"
        return "hands_open"


_gesture_engine: GestureEngine | None = None


def get_gesture_engine() -> GestureEngine:
    """Return the shared gesture engine singleton."""
    global _gesture_engine
    if _gesture_engine is None:
        _gesture_engine = GestureEngine()
    return _gesture_engine
