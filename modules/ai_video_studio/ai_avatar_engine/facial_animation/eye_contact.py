"""Eye contact — manage natural on/off-camera gaze patterns."""
from __future__ import annotations

import math
from typing import Any

from modules.ai_video_studio.editor_common import clamp


class EyeContact:
    """Produces gaze parameters that hold camera contact with breaks."""

    def __init__(self, contact_ratio: float = 0.7) -> None:
        self.contact_ratio = clamp(contact_ratio, 0.0, 1.0)

    def drive(self, *, t: float = 0.0) -> dict[str, Any]:
        """Return gaze at time ``t``: mostly center, occasional averted glance."""
        cycle = 4.0  # seconds per look-cycle
        phase = (t % cycle) / cycle
        if phase < self.contact_ratio:
            return {"gaze_x": 0.0, "gaze_y": 0.0, "contact": 1.0}
        # Averted glance drifts and returns.
        progress = (phase - self.contact_ratio) / max(1 - self.contact_ratio, 1e-6)
        x = 0.25 * math.sin(progress * math.pi * 2)
        y = 0.1 * math.sin(progress * math.pi * 3)
        return {"gaze_x": round(x, 3), "gaze_y": round(y, 3), "contact": 0.0}


_eye_contact: EyeContact | None = None


def get_eye_contact() -> EyeContact:
    global _eye_contact
    if _eye_contact is None:
        _eye_contact = EyeContact()
    return _eye_contact
