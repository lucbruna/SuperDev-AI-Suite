"""Facial landmarks — canonical landmark point names for the face."""
from __future__ import annotations

# Canonical 2D landmark keys shared across capture and animation.
LANDMARK_KEYS = (
    "left_eye", "right_eye", "left_eye_top", "right_eye_top", "left_eye_bottom", "right_eye_bottom",
    "left_brow", "right_brow", "left_brow_inner", "right_brow_inner",
    "nose", "nose_tip", "nose_bridge",
    "mouth_left", "mouth_right", "mouth_top", "mouth_bottom", "mouth_center",
    "left_cheek", "right_cheek", "chin", "forehead_center",
)


def empty_landmarks() -> dict[str, tuple[float, float]]:
    """Return a dict of every landmark key mapped to (0.5, 0.5)."""
    return {key: (0.5, 0.5) for key in LANDMARK_KEYS}
