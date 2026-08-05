"""Camera director — choose camera moves per shot."""
from __future__ import annotations

from typing import Any

_CAMERA_MOVES = {
    "close-up": {"position": (0, 1.6, 0.3), "focal": 85, "move": "static"},
    "wide shot": {"position": (0, 1.6, 6.0), "focal": 24, "move": "pan"},
    "drone": {"position": (0, 30, 40), "focal": 35, "move": "aerial"},
    "orbit": {"position": (4, 1.6, 0), "focal": 50, "move": "orbit"},
    "handheld": {"position": (0, 1.6, 2.0), "focal": 35, "move": "handheld"},
    "dolly": {"position": (0, 1.6, 4.0), "focal": 50, "move": "dolly_in"},
    "aerial": {"position": (0, 25, 30), "focal": 28, "move": "descend"},
    "low angle": {"position": (0, 0.4, 2.0), "focal": 24, "move": "tilt_up"},
}


class CameraDirector:
    """Maps a shot type to concrete camera parameters."""

    def direct(self, shot_type: str) -> dict[str, Any]:
        base = _CAMERA_MOVES.get(shot_type, _CAMERA_MOVES["wide shot"])
        return dict(base)

    def available_moves(self) -> list[str]:
        return list(_CAMERA_MOVES.keys())
