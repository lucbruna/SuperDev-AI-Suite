"""Face solver — inverts a landmark mesh into facial parameters."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.editor_common import clamp


class FaceSolver:
    """Estimates facial parameters from a landmark mesh (inverse mapping)."""

    def solve(self, landmarks: dict[str, tuple[float, float]]) -> dict[str, Any]:
        def _pt(key: str) -> tuple[float, float] | None:
            value = landmarks.get(key)
            return (float(value[0]), float(value[1])) if value else None

        mouth_t = _pt("mouth_top")
        mouth_b = _pt("mouth_bottom")
        mouth_l = _pt("mouth_left")
        mouth_r = _pt("mouth_right")
        eye_t = _pt("left_eye_top")
        eye_b = _pt("left_eye_bottom")
        brow = _pt("left_brow")
        eye = _pt("left_eye")

        mouth_open = clamp(abs(mouth_t[1] - mouth_b[1]) * 6.0) if mouth_t and mouth_b else 0.0
        smile = 0.0
        if mouth_l and mouth_r and mouth_t:
            mid_y = (mouth_l[1] + mouth_r[1]) / 2
            smile = clamp((mouth_t[1] - mid_y) * -8.0, -1.0, 1.0)
        eye_open = clamp(1.0 - abs(eye_t[1] - eye_b[1]) * 8.0) if eye_t and eye_b else 1.0
        brow_raise = clamp((eye[1] - brow[1]) * 5.0) if eye and brow else 0.0

        return {
            "mouth_open": round(mouth_open, 3),
            "smile": round(smile, 3),
            "eye_open": round(eye_open, 3),
            "brow_raise": round(brow_raise, 3),
        }


_face_solver: FaceSolver | None = None


def get_face_solver() -> FaceSolver:
    global _face_solver
    if _face_solver is None:
        _face_solver = FaceSolver()
    return _face_solver
