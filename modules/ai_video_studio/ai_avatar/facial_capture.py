"""Facial capture — extract facial animation parameters from a source.

Real capture requires a face-tracking backend (e.g. MediaPipe); when the
backend is unavailable the engine still works by accepting a landmarks
dictionary (a dict of ``{feature: [x, y]}`` points) or a raw frame and
deriving normalized parameters (brow raise, eye openness, mouth open,
smile) deterministically from simple heuristics.
"""
from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray


class FacialCapture:
    """Derive facial parameters from landmarks or a raw frame."""

    # Feature keys accepted from external trackers.
    FEATURES = ("left_eye", "right_eye", "left_eye_top", "right_eye_top",
                "left_brow", "right_brow", "nose", "mouth_left", "mouth_right",
                "mouth_top", "mouth_bottom")

    def capture_from_landmarks(self, landmarks: dict[str, list[float] | tuple[float, float]]) -> dict[str, Any]:
        """Map a ``{feature: [x, y]}`` landmark dict to animation params.

        All coordinates are expected in normalized space (0..1). Missing
        features fall back to neutral values.
        """
        def _pt(key: str) -> tuple[float, float] | None:
            value = landmarks.get(key)
            if value is None or len(value) < 2:
                return None
            return (float(value[0]), float(value[1]))

        mouth_l = _pt("mouth_left")
        mouth_r = _pt("mouth_right")
        mouth_t = _pt("mouth_top")
        mouth_b = _pt("mouth_bottom")
        eye_l = _pt("left_eye")
        eye_r = _pt("right_eye")

        mouth_open = 0.0
        if mouth_t and mouth_b:
            mouth_open = float(np.clip(abs(mouth_t[1] - mouth_b[1]) * 6.0, 0.0, 1.0))
        mouth_curve = 0.0
        if mouth_l and mouth_r:
            # Smile when mouth corners are above the midpoint of the lips.
            mid_y = (mouth_l[1] + mouth_r[1]) / 2.0
            mouth_curve = float(np.clip((mouth_l[1] - mid_y) * -8.0, -1.0, 1.0))

        eye_open = 1.0
        if eye_l and eye_r:
            spread = abs(eye_l[0] - eye_r[0]) or 1e-6
            left_h = _pt("left_eye_top") or eye_l
            right_h = _pt("right_eye_top") or eye_r
            openness = (abs(left_h[1] - eye_l[1]) + abs(right_h[1] - eye_r[1])) / 2.0
            eye_open = float(np.clip(openness / (spread * 0.35), 0.0, 1.0))

        brow_raise = 0.0
        brow_l = _pt("left_brow")
        if brow_l and eye_l:
            brow_raise = float(np.clip((eye_l[1] - brow_l[1]) * 5.0, 0.0, 1.0))

        return {
            "source": "landmarks",
            "brow_raise": round(brow_raise, 3),
            "brow_frown": 0.0,
            "eye_open": round(max(eye_open, 0.05), 3),
            "mouth_open": round(mouth_open, 3),
            "mouth_curve": round(mouth_curve, 3),
            "head_tilt": 0.0,
            "confidence": 0.5,
        }

    def capture_from_frame(self, frame: NDArray[np.floating] | NDArray[np.uint8]) -> dict[str, Any]:
        """Fallback capture: derive crude parameters from frame brightness.

        This keeps the pipeline functional without a face-tracking backend:
        the mouth-open estimate is driven by the center-region luminance of
        the lower face area, and the smile estimate by overall warmth.
        """
        arr = np.asarray(frame, dtype=np.float64)
        if arr.ndim != 3 or arr.shape[2] < 3:
            return self.capture_from_landmarks({})
        h, w = arr.shape[:2]
        # Lower-center region → mouth zone.
        zone = arr[int(h * 0.55):int(h * 0.8), int(w * 0.3):int(w * 0.7), :3]
        if zone.size == 0:
            zone = arr[:, :, :3]
        mean_rgb = zone.mean(axis=(0, 1))
        luminance = float(0.299 * mean_rgb[0] + 0.587 * mean_rgb[1] + 0.114 * mean_rgb[2]) / 255.0
        # A bright mouth region suggests an open mouth in a talking head.
        mouth_open = float(np.clip((luminance - 0.35) * 2.0, 0.0, 1.0))
        warmth = float(np.clip((mean_rgb[0] - mean_rgb[2]) / 255.0 * 2.0, 0.0, 1.0))
        return {
            "source": "frame",
            "brow_raise": 0.0,
            "brow_frown": 0.0,
            "eye_open": 0.9,
            "mouth_open": round(mouth_open, 3),
            "mouth_curve": round(warmth - 0.2, 3),
            "head_tilt": 0.0,
            "confidence": 0.25,
        }

    def available_backend(self) -> bool:
        """True when a real face-tracking backend is installed."""
        try:
            import cv2  # noqa: F401

            return True
        except Exception:  # noqa: BLE001
            return False


_facial_capture: FacialCapture | None = None


def get_facial_capture() -> FacialCapture:
    """Return the shared facial-capture singleton."""
    global _facial_capture
    if _facial_capture is None:
        _facial_capture = FacialCapture()
    return _facial_capture
