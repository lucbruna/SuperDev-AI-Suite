"""Emotional blending — interpolate between emotion presets over time."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.editor_common import clamp, lerp, smoothstep


class EmotionalBlending:
    """Blends two named emotions (or returns an emotion timeline)."""

    def blend(self, a: str, b: str, t: float) -> dict[str, Any]:
        from modules.ai_video_studio.ai_avatar_engine.emotions.emotion_engine import (
            get_emotion_engine,
        )

        ea = get_emotion_engine().get(a)
        eb = get_emotion_engine().get(b)
        t = clamp(t)
        return {
            "name": a if t < 0.5 else b,
            "facial": {k: round(lerp(ea.facial.get(k, 0.0), eb.facial.get(k, 0.0), t), 3)
                       for k in set(ea.facial) | set(eb.facial)},
            "body": {k: round(lerp(ea.body.get(k, 0.0), eb.body.get(k, 0.0), t), 3)
                     for k in set(ea.body) | set(eb.body)},
            "voice": {k: round(lerp(float(ea.voice.get(k, 0.0)), float(eb.voice.get(k, 0.0)), t), 3)
                      for k in set(ea.voice) | set(eb.voice)},
            "t": round(t, 3),
        }

    def timeline(self, segments: list[dict[str, Any]], *, duration: float,
                 fps: int = 24) -> list[dict[str, Any]]:
        """Per-frame emotion timeline from ``{start, end, emotion}`` segments."""
        frame_count = max(1, int(duration * fps))
        ease = max(2, int(0.15 * fps))
        frames: list[dict[str, Any]] = []
        for f in range(frame_count):
            t = f / fps
            current = next((s for s in segments if s["start"] <= t < s["end"]), segments[-1])
            state = self.blend(current["emotion"], current["emotion"], 1.0)
            idx = segments.index(current)
            if idx > 0:
                prev = segments[idx - 1]
                dist = t - prev["end"]
                if 0 <= dist < ease / fps:
                    state = self.blend(prev["emotion"], current["emotion"],
                                       smoothstep(0.0, ease / fps, dist))
            state["frame"] = f
            state["time"] = round(t, 3)
            frames.append(state)
        return frames


_emotional_blending: EmotionalBlending | None = None


def get_emotional_blending() -> EmotionalBlending:
    global _emotional_blending
    if _emotional_blending is None:
        _emotional_blending = EmotionalBlending()
    return _emotional_blending
