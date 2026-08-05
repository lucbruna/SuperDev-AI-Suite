"""Facial rig — the parameter space every controller writes into."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.editor_common import clamp

# Neutral baseline of every facial parameter.
NEUTRAL_FACE: dict[str, float] = {
    "smile": 0.0, "mouth_open": 0.0, "mouth_width": 0.0, "mouth_round": 0.0,
    "jaw_open": 0.0, "lips_pressed": 0.0,
    "cheek_raise": 0.0, "nose_wrinkle": 0.0,
    "brow_raise": 0.0, "brow_frown": 0.0, "brow_inner": 0.0,
    "forehead_raise": 0.0, "blink_left": 0.0, "blink_right": 0.0,
    "gaze_x": 0.0, "gaze_y": 0.0, "head_tilt": 0.0,
}


class FacialRig:
    """Applies controller deltas on top of the neutral face baseline."""

    def neutral(self) -> dict[str, float]:
        return dict(NEUTRAL_FACE)

    def apply(self, *deltas: dict[str, Any]) -> dict[str, Any]:
        """Merge several controller outputs into one clamped parameter set."""
        result = self.neutral()
        for delta in deltas:
            for key, value in (delta or {}).items():
                if key in result:
                    result[key] = clamp(float(value), -1.0, 1.0)
        return result


_facial_rig: FacialRig | None = None


def get_facial_rig() -> FacialRig:
    global _facial_rig
    if _facial_rig is None:
        _facial_rig = FacialRig()
    return _facial_rig
