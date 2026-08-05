"""Body capture — extract body/pose parameters from a source.

Mirrors the facial-capture design: a full pose backend (MediaPipe Pose,
OpenPose) can feed a ``{joint: [x, y]}`` landmarks dict, and a lightweight
frame-based fallback keeps the module functional offline. Outputs are
normalized parameters consumed by :mod:`ai_avatar.digital_human`.
"""
from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

# Joint keys accepted from external pose trackers.
JOINTS = ("nose", "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
          "left_wrist", "right_wrist", "left_hip", "right_hip", "left_knee", "right_knee")


class BodyCapture:
    """Derive pose parameters from keypoints or a raw frame."""

    def capture_from_keypoints(self, keypoints: dict[str, list[float] | tuple[float, float]]) -> dict[str, Any]:
        """Map a ``{joint: [x, y]}`` keypoint dict to pose params (normalized 0..1)."""
        def _pt(key: str) -> tuple[float, float] | None:
            value = keypoints.get(key)
            if value is None or len(value) < 2:
                return None
            return (float(value[0]), float(value[1]))

        shoulder_l = _pt("left_shoulder")
        shoulder_r = _pt("right_shoulder")
        wrist_l = _pt("left_wrist")
        wrist_r = _pt("right_wrist")
        hip_l = _pt("left_hip")
        hip_r = _pt("right_hip")

        # Arm lift: how far the wrists are above the shoulders.
        arm_left = arm_right = 0.0
        if shoulder_l and wrist_l:
            arm_left = float(np.clip((shoulder_l[1] - wrist_l[1]) * 3.0, -1.0, 1.0))
        if shoulder_r and wrist_r:
            arm_right = float(np.clip((shoulder_r[1] - wrist_r[1]) * 3.0, -1.0, 1.0))

        # Lean: horizontal deviation of the shoulders from the hips.
        lean = 0.0
        if shoulder_l and shoulder_r and hip_l and hip_r:
            shoulder_mid = ((shoulder_l[0] + shoulder_r[0]) / 2.0, (shoulder_l[1] + shoulder_r[1]) / 2.0)
            hip_mid = ((hip_l[0] + hip_r[0]) / 2.0, (hip_l[1] + hip_r[1]) / 2.0)
            lean = float(np.clip((shoulder_mid[0] - hip_mid[0]) * 3.0, -1.0, 1.0))

        return {
            "source": "keypoints",
            "arm_left": round(arm_left, 3),
            "arm_right": round(arm_right, 3),
            "lean": round(lean, 3),
            "head": "neutral",
            "confidence": 0.5,
        }

    def capture_from_frame(self, frame: NDArray[np.floating] | NDArray[np.uint8]) -> dict[str, Any]:
        """Frame-based fallback: center-of-mass driven neutral pose."""
        arr = np.asarray(frame, dtype=np.float64)
        if arr.ndim != 3 or arr.shape[2] < 3:
            return self.capture_from_keypoints({})
        h, w = arr.shape[:2]
        # Brightness centroid of the upper half suggests head position/lean.
        upper = arr[: int(h * 0.5), :, :3]
        gray = 0.299 * upper[..., 0] + 0.587 * upper[..., 1] + 0.114 * upper[..., 2]
        total = gray.sum() + 1e-9
        ys, xs = np.mgrid[0:upper.shape[0], 0:upper.shape[1]]
        cx = float((xs * gray).sum() / total) / w
        lean = float(np.clip((cx - 0.5) * 2.0, -1.0, 1.0))
        return {
            "source": "frame",
            "arm_left": 0.0,
            "arm_right": 0.0,
            "lean": round(lean, 3),
            "head": "neutral",
            "confidence": 0.25,
        }

    def available_backend(self) -> bool:
        """True when a real pose-tracking backend is installed."""
        try:
            import cv2  # noqa: F401

            return True
        except Exception:  # noqa: BLE001
            return False


_body_capture: BodyCapture | None = None


def get_body_capture() -> BodyCapture:
    """Return the shared body-capture singleton."""
    global _body_capture
    if _body_capture is None:
        _body_capture = BodyCapture()
    return _body_capture
