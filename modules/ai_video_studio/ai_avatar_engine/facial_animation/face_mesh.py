"""Face mesh — builds a lightweight landmark mesh from parameters."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_avatar_engine.facial_animation.facial_landmarks import (
    empty_landmarks,
)


class FaceMesh:
    """Produces a normalized 2D landmark mesh from facial parameters.

    The mesh is a dict of landmark keys → (x, y) in normalized space (0..1),
    deformed by the current expression parameters (smile, mouth_open, brows,
    eyes).
    """

    def build(self, params: dict[str, Any] | None = None) -> dict[str, tuple[float, float]]:
        params = params or {}
        mesh = empty_landmarks()

        cx, cy = 0.5, 0.5
        eye_open = 1.0 - 0.6 * float(params.get("eye_open_delta", 0.0))
        smile = float(params.get("smile", 0.0))
        mouth_open = float(params.get("mouth_open", 0.0))
        brow_raise = float(params.get("brow_raise", 0.0))

        # Eyes (openness controls vertical gap).
        eye_y_top = cy - 0.09 - (1 - eye_open) * 0.04
        eye_y_bot = cy - 0.03 + (1 - eye_open) * 0.04
        mesh["left_eye"] = (cx - 0.11, (eye_y_top + eye_y_bot) / 2)
        mesh["right_eye"] = (cx + 0.11, (eye_y_top + eye_y_bot) / 2)
        mesh["left_eye_top"] = (cx - 0.11, eye_y_top)
        mesh["right_eye_top"] = (cx + 0.11, eye_y_top)
        mesh["left_eye_bottom"] = (cx - 0.11, eye_y_bot)
        mesh["right_eye_bottom"] = (cx + 0.11, eye_y_bot)

        # Brows.
        brow_y = cy - 0.14 - brow_raise * 0.04
        mesh["left_brow"] = (cx - 0.11, brow_y)
        mesh["right_brow"] = (cx + 0.11, brow_y)
        mesh["left_brow_inner"] = (cx - 0.06, brow_y + 0.01)
        mesh["right_brow_inner"] = (cx + 0.06, brow_y + 0.01)

        # Nose.
        mesh["nose_bridge"] = (cx, cy - 0.02)
        mesh["nose_tip"] = (cx, cy + 0.06)
        mesh["nose"] = (cx, cy + 0.05)

        # Mouth (smile lifts corners, openness grows height).
        corner_y = cy + 0.16 - smile * 0.03
        mesh["mouth_left"] = (cx - 0.09, corner_y)
        mesh["mouth_right"] = (cx + 0.09, corner_y)
        mesh["mouth_top"] = (cx, cy + 0.14 - mouth_open * 0.05)
        mesh["mouth_bottom"] = (cx, cy + 0.18 + mouth_open * 0.08)
        mesh["mouth_center"] = (cx, (mesh["mouth_top"][1] + mesh["mouth_bottom"][1]) / 2)

        # Cheeks / chin / forehead.
        mesh["left_cheek"] = (cx - 0.17, cy + 0.06)
        mesh["right_cheek"] = (cx + 0.17, cy + 0.06)
        mesh["chin"] = (cx, cy + 0.24)
        mesh["forehead_center"] = (cx, cy - 0.20)
        return mesh


_face_mesh: FaceMesh | None = None


def get_face_mesh() -> FaceMesh:
    global _face_mesh
    if _face_mesh is None:
        _face_mesh = FaceMesh()
    return _face_mesh
