"""Facial engine — composes controllers into per-frame facial parameters."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_avatar_engine.facial_animation.blink_controller import (
    get_blink_controller,
)
from modules.ai_video_studio.ai_avatar_engine.facial_animation.cheeks_controller import (
    get_cheeks_controller,
)
from modules.ai_video_studio.ai_avatar_engine.facial_animation.eyebrow_controller import (
    get_eyebrow_controller,
)
from modules.ai_video_studio.ai_avatar_engine.facial_animation.face_mesh import get_face_mesh
from modules.ai_video_studio.ai_avatar_engine.facial_animation.facial_rig import get_facial_rig
from modules.ai_video_studio.ai_avatar_engine.facial_animation.forehead_controller import (
    get_forehead_controller,
)
from modules.ai_video_studio.ai_avatar_engine.facial_animation.gaze_controller import (
    get_gaze_controller,
)
from modules.ai_video_studio.ai_avatar_engine.facial_animation.jaw_controller import (
    get_jaw_controller,
)
from modules.ai_video_studio.ai_avatar_engine.facial_animation.lips_controller import (
    get_lips_controller,
)
from modules.ai_video_studio.ai_avatar_engine.facial_animation.nose_controller import (
    get_nose_controller,
)
from modules.ai_video_studio.ai_avatar_engine.facial_animation.smile_controller import (
    get_smile_controller,
)


class FacialEngine:
    """Runs the face rig: baseline + controllers → per-frame parameter set."""

    def compose(
        self,
        *,
        t: float = 0.0,
        smile: float = 0.0,
        mouth_open: float = 0.0,
        brow_raise: float = 0.0,
        brow_frown: float = 0.0,
        target_x: float = 0.0,
        target_y: float = 0.0,
        forced_blink: float = 0.0,
        controllers: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Blend controller outputs into one clamped facial parameter set."""
        rig = get_facial_rig()
        gaze = get_gaze_controller().drive(t=t, target_x=target_x, target_y=target_y)

        extra = list(controllers or [])

        # Built-in controllers feed the same rig.
        extra += [
            get_smile_controller().drive(amount=smile),
            get_jaw_controller().drive(open=mouth_open),
            get_lips_controller().drive(width=smile * 0.4),
            get_eyebrow_controller().drive(raise_level=brow_raise, frown=brow_frown),
            get_forehead_controller().drive(raise_level=brow_raise * 0.5),
            get_cheeks_controller().drive(raise_level=max(0.0, smile) * 0.5),
            get_nose_controller().drive(wrinkle=brow_frown * 0.4),
            get_blink_controller().drive(t=t, forced=forced_blink),
            gaze,
        ]
        params = rig.apply(*extra)
        params["frame_time"] = round(t, 3)
        return params

    def mesh(self, params: dict[str, Any]) -> dict[str, tuple[float, float]]:
        """Build the landmark mesh for a facial parameter set."""
        return get_face_mesh().build(params)


_facial_engine: FacialEngine | None = None


def get_facial_engine() -> FacialEngine:
    """Return the shared facial engine singleton."""
    global _facial_engine
    if _facial_engine is None:
        _facial_engine = FacialEngine()
    return _facial_engine
