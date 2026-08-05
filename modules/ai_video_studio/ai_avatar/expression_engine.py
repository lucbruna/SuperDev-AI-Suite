"""Emotional expression engine — map emotions to facial animation params.

Each emotion is expressed as a set of facial parameters (brow raise, eye
open, mouth open/curve, head tilt...). ``interpolate`` eases between two
expressions so presenters transition naturally between emotional states.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from modules.ai_video_studio.editor_common import clamp, lerp, smoothstep


@dataclass(frozen=True)
class Expression:
    """A named facial expression as normalized animation parameters."""

    name: str
    brow_raise: float = 0.0       # 0..1 raised brows
    brow_frown: float = 0.0       # 0..1 furrowed brows
    eye_open: float = 1.0         # 0..1 eyelid openness
    mouth_open: float = 0.0       # 0..1 jaw openness
    mouth_curve: float = 0.0      # -1..1 frown..smile
    head_tilt: float = 0.0        # degrees
    intensity: float = 1.0        # global strength

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "brow_raise": round(self.brow_raise, 3),
            "brow_frown": round(self.brow_frown, 3),
            "eye_open": round(self.eye_open, 3),
            "mouth_open": round(self.mouth_open, 3),
            "mouth_curve": round(self.mouth_curve, 3),
            "head_tilt": round(self.head_tilt, 3),
            "intensity": round(self.intensity, 3),
        }


EXPRESSIONS: dict[str, Expression] = {
    "neutral": Expression("neutral", mouth_open=0.0, mouth_curve=0.0),
    "happy": Expression("happy", brow_raise=0.3, eye_open=0.9, mouth_open=0.25, mouth_curve=0.8),
    "sad": Expression("sad", brow_frown=0.4, eye_open=0.7, mouth_open=0.1, mouth_curve=-0.5, head_tilt=-4.0),
    "angry": Expression("angry", brow_frown=0.9, eye_open=0.8, mouth_open=0.2, mouth_curve=-0.4, head_tilt=2.0),
    "surprised": Expression("surprised", brow_raise=1.0, eye_open=1.0, mouth_open=0.9, mouth_curve=0.1),
    "fear": Expression("fear", brow_raise=0.8, brow_frown=0.5, eye_open=1.0, mouth_open=0.6, mouth_curve=-0.3),
    "disgust": Expression("disgust", brow_frown=0.7, eye_open=0.5, mouth_open=0.3, mouth_curve=-0.6),
    "excited": Expression("excited", brow_raise=0.7, eye_open=1.0, mouth_open=0.5, mouth_curve=0.9, head_tilt=4.0),
    "calm": Expression("calm", brow_raise=0.1, eye_open=0.8, mouth_open=0.05, mouth_curve=0.2),
    "thinking": Expression("thinking", brow_frown=0.5, eye_open=0.6, mouth_open=0.05, mouth_curve=-0.1, head_tilt=-6.0),
}

VALID_EXPRESSIONS = tuple(EXPRESSIONS)


class ExpressionEngine:
    """Resolve emotions to facial parameters, with easing between states."""

    def get(self, name: str) -> Expression:
        if name not in EXPRESSIONS:
            raise KeyError(f"unknown expression '{name}'")
        return EXPRESSIONS[name]

    def names(self) -> list[str]:
        return list(EXPRESSIONS)

    def apply(self, name: str, *, intensity: float = 1.0) -> dict[str, Any]:
        """Return the parameter dict for an emotion at a given intensity."""
        base = self.get(name)
        scaled = Expression(
            name=base.name,
            brow_raise=base.brow_raise * intensity,
            brow_frown=base.brow_frown * intensity,
            eye_open=lerp(1.0, base.eye_open, intensity),
            mouth_open=base.mouth_open * intensity,
            mouth_curve=base.mouth_curve * intensity,
            head_tilt=base.head_tilt * intensity,
            intensity=clamp(intensity),
        )
        return scaled.to_dict()

    def interpolate(self, a: str, b: str, t: float) -> dict[str, Any]:
        """Ease between two named expressions (``t`` 0→1)."""
        ea, eb = self.get(a), self.get(b)
        t = clamp(t)
        return {
            "name": a if t < 0.5 else b,
            "brow_raise": round(lerp(ea.brow_raise, eb.brow_raise, t), 3),
            "brow_frown": round(lerp(ea.brow_frown, eb.brow_frown, t), 3),
            "eye_open": round(lerp(ea.eye_open, eb.eye_open, t), 3),
            "mouth_open": round(lerp(ea.mouth_open, eb.mouth_open, t), 3),
            "mouth_curve": round(lerp(ea.mouth_curve, eb.mouth_curve, t), 3),
            "head_tilt": round(lerp(ea.head_tilt, eb.head_tilt, t), 3),
            "intensity": round(lerp(ea.intensity, eb.intensity, t), 3),
        }

    def timeline(self, segments: list[dict[str, Any]], *, duration: float, fps: int = 24) -> list[dict[str, Any]]:
        """Build a per-frame expression timeline from ``{start, end, expression}`` segments.

        Eases between consecutive expressions over a small overlap so the
        presenter's face transitions smoothly.
        """
        frame_count = max(1, int(duration * fps))
        easing = max(2, int(0.15 * fps))  # 150ms cross-fade
        segments = [s for s in segments if s.get("expression") in EXPRESSIONS]
        if not segments:
            segments = [{"start": 0.0, "end": duration, "expression": "neutral"}]

        frames: list[dict[str, Any]] = []
        for f in range(frame_count):
            t = f / fps
            current = next((s for s in segments if s["start"] <= t < s["end"]), segments[-1])
            params = self.apply(current["expression"])
            # Ease from the previous segment if we are near its boundary.
            idx = segments.index(current)
            if idx > 0:
                prev = segments[idx - 1]
                dist_from_prev = t - prev["end"]
                if 0 <= dist_from_prev < easing / fps:
                    params = self.interpolate(prev["expression"], current["expression"],
                                              smoothstep(0.0, easing / fps, dist_from_prev))
            params["frame"] = f
            params["time"] = round(t, 3)
            frames.append(params)
        return frames


_expression_engine: ExpressionEngine | None = None


def get_expression_engine() -> ExpressionEngine:
    """Return the shared expression engine singleton."""
    global _expression_engine
    if _expression_engine is None:
        _expression_engine = ExpressionEngine()
    return _expression_engine
