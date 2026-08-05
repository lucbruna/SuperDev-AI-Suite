"""Body synchronization — fuse speech, emotion and gesture into one timeline.

The body-sync stage takes a script's per-frame expression and gesture
timelines and produces a single per-frame parameter dict (head pose, arm
lifts, lean, mouth, brows) that the digital-human renderer draws. It also
synthesizes a simple mouth-motion envelope from the text cadence so the
presenter "speaks" without requiring a full phoneme pipeline.
"""
from __future__ import annotations

import math
from typing import Any

from modules.ai_video_studio.ai_avatar.expression_engine import get_expression_engine
from modules.ai_video_studio.ai_avatar.gesture_engine import get_gesture_engine
from modules.ai_video_studio.editor_common import clamp


class BodySync:
    """Synchronize expression + gesture timelines into final frame params."""

    def sync(
        self,
        text: str,
        *,
        duration: float,
        fps: int = 24,
        expressions: list[dict[str, Any]] | None = None,
        gestures: list[dict[str, Any]] | None = None,
        base_expression: str = "neutral",
    ) -> dict[str, Any]:
        """Merge everything into a per-frame animation timeline."""
        duration = max(0.5, duration)
        frame_count = max(1, int(duration * fps))

        expression_engine = get_expression_engine()
        gesture_engine = get_gesture_engine()

        expr_frames = expressions or expression_engine.timeline(
            [{"start": 0.0, "end": duration, "expression": base_expression}],
            duration=duration, fps=fps,
        )
        gest_frames = gestures or gesture_engine.plan_for_text(text, duration=duration, fps=fps)

        frames: list[dict[str, Any]] = []
        for f in range(frame_count):
            t = f / fps
            expr = expr_frames[f] if f < len(expr_frames) else expr_frames[-1]
            gest = gest_frames[f] if f < len(gest_frames) else gest_frames[-1]
            speech = self._speech_envelope(text, t, duration)

            frames.append({
                "frame": f,
                "time": round(t, 3),
                "brow_raise": expr["brow_raise"],
                "brow_frown": expr["brow_frown"],
                "eye_open": expr["eye_open"],
                "mouth_open": max(expr["mouth_open"], speech),
                "mouth_curve": expr["mouth_curve"],
                "head_tilt": expr["head_tilt"] + self._head_bob(t),
                "arm_left": gest["arm_left"],
                "arm_right": gest["arm_right"],
                "lean": gest["lean"],
                "head_gesture": gest["head"],
                "emotion": expr.get("name", base_expression),
                "gesture": gest.get("gesture", "neutral"),
            })

        return {
            "duration": round(duration, 3),
            "fps": fps,
            "frames": frame_count,
            "timeline": frames,
        }

    @staticmethod
    def _speech_envelope(text: str, t: float, duration: float) -> float:
        """Pseudo mouth-motion from text cadence: words pulse around syllables."""
        word_count = max(len(text.split()), 1)
        words_per_sec = word_count / max(duration, 1e-6)
        # Estimate syllable pulses: 1.7 syllables per word on average.
        pulse = 1.7 * words_per_sec
        envelope = 0.5 + 0.5 * math.sin(2 * math.pi * pulse * t + math.sin(t * 3.0))
        # Envelope follows sentence emphasis: stronger at sentence starts.
        sentence_len = 6.0
        emphasis = math.exp(-((t % sentence_len) / 2.0))
        return clamp(0.15 + 0.5 * envelope * (0.4 + 0.6 * emphasis))

    @staticmethod
    def _head_bob(t: float) -> float:
        """Subtle constant head bob so the presenter feels alive."""
        return 1.5 * math.sin(t * 2.1) + 0.8 * math.sin(t * 5.3)


_body_sync: BodySync | None = None


def get_body_sync() -> BodySync:
    """Return the shared body-sync singleton."""
    global _body_sync
    if _body_sync is None:
        _body_sync = BodySync()
    return _body_sync
