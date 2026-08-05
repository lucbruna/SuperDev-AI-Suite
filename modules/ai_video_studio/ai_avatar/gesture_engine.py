"""Gesture engine — automatic body gestures for virtual presenters.

Plans a gesture timeline from a script: gestures (nod, shake, point, wave,
thumbs-up, cross arms, hands open, shrug, lean) are triggered by keywords,
punctuation and sentence boundaries, and returned as per-frame parameters
consumed by the digital-human renderer.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any

from modules.ai_video_studio.editor_common import clamp


@dataclass(frozen=True)
class Gesture:
    """A named body gesture."""

    name: str
    arm_left: float = 0.0       # -1..1 left arm lift
    arm_right: float = 0.0      # -1..1 right arm lift
    lean: float = 0.0           # -1..1 body lean
    head: str = "neutral"       # nod | shake | tilt | neutral
    amplitude: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "arm_left": round(self.arm_left, 3),
            "arm_right": round(self.arm_right, 3),
            "lean": round(self.lean, 3),
            "head": self.head,
            "amplitude": round(self.amplitude, 3),
        }


GESTURES: dict[str, Gesture] = {
    "neutral": Gesture("neutral", 0.0, 0.0, 0.0, "neutral"),
    "point": Gesture("point", 0.7, 0.3, 0.1, "tilt"),
    "wave": Gesture("wave", 0.8, 0.2, 0.0, "neutral"),
    "nod": Gesture("nod", 0.2, 0.2, 0.0, "nod"),
    "shake": Gesture("shake", 0.2, 0.2, 0.0, "shake"),
    "thumbs_up": Gesture("thumbs_up", 0.9, 0.1, -0.1, "tilt"),
    "cross_arms": Gesture("cross_arms", 0.35, 0.35, 0.05, "neutral"),
    "hands_open": Gesture("hands_open", 0.5, 0.5, 0.0, "neutral"),
    "shrug": Gesture("shrug", 0.5, 0.5, -0.2, "neutral"),
    "lean": Gesture("lean", 0.1, 0.1, 0.4, "tilt"),
}

# keyword → gesture triggers
_TRIGGERS: dict[str, str] = {
    "important": "point", "key": "point", "note": "point", "look": "point",
    "hello": "wave", "welcome": "wave", "goodbye": "wave", "hi ": "wave",
    "agree": "nod", "yes": "nod", "correct": "nod", "right": "nod",
    "no": "shake", "wrong": "shake", "never": "shake", "not": "shake",
    "great": "thumbs_up", "awesome": "thumbs_up", "amazing": "thumbs_up", "perfect": "thumbs_up",
    "maybe": "shrug", "perhaps": "shrug", "unsure": "shrug", "depends": "shrug",
    "imagine": "hands_open", "picture": "hands_open", "consider": "hands_open",
}


class GestureEngine:
    """Plan automatic gestures from a script or explicit cues."""

    def names(self) -> list[str]:
        return list(GESTURES)

    def get(self, name: str) -> Gesture:
        if name not in GESTURES:
            raise KeyError(f"unknown gesture '{name}'")
        return GESTURES[name]

    def apply(self, name: str, *, amplitude: float = 1.0) -> dict[str, Any]:
        g = self.get(name)
        return Gesture(
            name=g.name, arm_left=g.arm_left * amplitude, arm_right=g.arm_right * amplitude,
            lean=g.lean * amplitude, head=g.head, amplitude=clamp(amplitude),
        ).to_dict()

    def plan_for_text(self, text: str, *, duration: float, fps: int = 24) -> list[dict[str, Any]]:
        """Build a per-frame gesture timeline by scanning the script.

        Sentences starting with a trigger word (or containing ``!`` / ``?``)
        receive an emphasis gesture; the rest use neutral or open hands.
        """
        frame_count = max(1, int(duration * fps))
        sentences = re.split(r"(?<=[.!?])\s+", text.strip()) or [text]
        sentence_count = max(len(sentences), 1)

        frames: list[dict[str, Any]] = []
        for f in range(frame_count):
            t = f / fps
            norm = t / max(duration, 1e-6)
            sent_idx = min(int(norm * sentence_count), sentence_count - 1)
            sentence = sentences[sent_idx].lower()

            gesture = self._gesture_for_sentence(sentence)
            base = self.get(gesture)
            # subtle amplitude modulation keeps it organic
            amp = 0.75 + 0.25 * abs(math.sin(f / fps * 1.7))
            frames.append({
                "frame": f, "time": round(t, 3), "gesture": gesture,
                "arm_left": round(base.arm_left * amp, 3),
                "arm_right": round(base.arm_right * amp, 3),
                "lean": round(base.lean * amp, 3),
                "head": base.head,
            })
        return frames

    def plan_for_scene(self, scene_type: str, *, duration: float, fps: int = 24) -> list[dict[str, Any]]:
        """Default gesture plan for a scene type (intro → wave, outro → wave...)."""
        default = {
            "intro": "wave", "title_card": "neutral", "content": "hands_open",
            "highlight": "point", "outro": "wave", "b_roll": "neutral",
            "credits": "neutral", "transition": "neutral",
        }.get(scene_type, "hands_open")
        return self.plan_for_text(_TRIGGER_SENTENCES.get(default, "Thanks for watching."),
                                  duration=duration, fps=fps)

    @staticmethod
    def _gesture_for_sentence(sentence: str) -> str:
        # Keyword triggers take priority so "Hello!" waves rather than points.
        for word, gesture in _TRIGGERS.items():
            if word in sentence:
                return gesture
        if sentence.endswith("!") or sentence.endswith("?"):
            return "point"
        return "hands_open"


# Sentences that produce each default gesture (used by plan_for_scene).
_TRIGGER_SENTENCES: dict[str, str] = {
    "wave": "Hello and welcome!",
    "point": "This is the key point!",
    "hands_open": "Picture this in your mind.",
    "nod": "Yes, that is correct.",
    "shake": "No, that is not right.",
    "thumbs_up": "That is great, perfect.",
    "shrug": "Maybe, perhaps it depends.",
}


_gesture_engine: GestureEngine | None = None


def get_gesture_engine() -> GestureEngine:
    """Return the shared gesture engine singleton."""
    global _gesture_engine
    if _gesture_engine is None:
        _gesture_engine = GestureEngine()
    return _gesture_engine
