"""Digital human renderer — draws a stylized presenter and encodes real media.

This is the Volume 6 renderer: it turns an actor + per-frame animation
timeline into a real MP4 (or a PNG still). The presenter is drawn with PIL
— head, hair, eyes that blink, brows, a mouth whose openness/curve follows
the timeline, a torso dressed from the wardrobe, and arms that gesture —
so the output is an actual video file, not metadata.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import numpy as np

from modules.ai_video_studio.ai_avatar.actor_library import VirtualActor
from modules.ai_video_studio.ai_avatar.wardrobe import get_wardrobe
from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.editor_common import clamp
from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
from modules.ai_video_studio.media.render import render_sim_frames


class DigitalHumanRenderer:
    """Renders virtual presenters into real videos and stills."""

    def __init__(self, width: int = 640, height: int = 360) -> None:
        if width <= 0 or height <= 0:
            raise ValidationError("dimensions must be positive")
        self.width = width
        self.height = height

    # ── Public API ────────────────────────────────────────────────
    def render_video(
        self,
        actor: VirtualActor,
        timeline: list[dict[str, Any]],
        *,
        fps: int = 24,
        outfit: str | None = None,
        output_path: str | Path | None = None,
        on_frame: Callable[[int, int], None] | None = None,
    ) -> dict[str, Any]:
        """Render a presenter video from an animation timeline."""
        if not timeline:
            raise ValidationError("timeline must not be empty", field="timeline")
        if fps <= 0:
            raise ValidationError("fps must be positive", field="fps")

        out = Path(output_path or unique_filename(get_subsystem_dir("avatars"), f"{actor.id}_presenter", "mp4"))
        clothing = get_wardrobe().select(outfit or actor.default_outfit, style=actor.style)
        total = len(timeline)

        def make_frame(i: int) -> np.ndarray:
            params = timeline[i] if i < len(timeline) else timeline[-1]
            frame = self._draw_frame(actor, params, clothing)
            if on_frame is not None:
                on_frame(i + 1, total)
            return frame

        result = render_sim_frames(make_frame, out, frames=total, fps=fps)
        result["actor"] = actor.id
        result["style"] = actor.style
        result["dimension"] = actor.dimension
        result["outfit"] = clothing["name"]
        result["frames"] = total
        return result

    def render_still(
        self,
        actor: VirtualActor,
        params: dict[str, Any] | None = None,
        *,
        outfit: str | None = None,
        output_path: str | Path | None = None,
    ) -> Path:
        """Render a single presenter frame to PNG."""
        out = Path(output_path or unique_filename(get_subsystem_dir("avatars"), f"{actor.id}_portrait", "png"))
        clothing = get_wardrobe().select(outfit or actor.default_outfit, style=actor.style)
        frame = self._draw_frame(actor, params or {}, clothing)
        from PIL import Image

        out.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(frame).save(out, format="PNG")
        return out

    # ── Frame drawing ─────────────────────────────────────────────
    def _draw_frame(self, actor: VirtualActor, params: dict[str, Any], clothing: dict[str, Any]) -> np.ndarray:
        from PIL import Image, ImageDraw

        w, h = self.width, self.height
        img = Image.new("RGB", (w, h), "#0f172a")
        draw = ImageDraw.Draw(img)

        # Stage floor + backdrop gradient feel.
        draw.rectangle([0, int(h * 0.82), w, h], fill="#1e293b")

        skin = actor.skin_tone
        hair = actor.hair_color

        mouth_open = clamp(float(params.get("mouth_open", 0.0)))
        mouth_curve = clamp(float(params.get("mouth_curve", 0.0)), -1.0, 1.0)
        eye_open = clamp(float(params.get("eye_open", 1.0)))
        brow_raise = clamp(float(params.get("brow_raise", 0.0)))
        brow_frown = clamp(float(params.get("brow_frown", 0.0)))
        arm_left = clamp(float(params.get("arm_left", 0.0)), -1.0, 1.0)
        arm_right = clamp(float(params.get("arm_right", 0.0)), -1.0, 1.0)
        lean = clamp(float(params.get("lean", 0.0)), -1.0, 1.0)
        head_tilt = float(params.get("head_tilt", 0.0))

        cx = w / 2 + lean * 20
        cy_head = int(h * 0.36)
        head_r = int(w * 0.16)
        # Head tilt shifts the facial features sideways (rotation illusion).
        tilt_shift = clamp(head_tilt / 12.0, -1.0, 1.0) * head_r * 0.35
        fcx = cx + tilt_shift

        # Head (ellipse keeps tilt cheap).
        draw.ellipse([cx - head_r, cy_head - head_r, cx + head_r, cy_head + head_r],
                     fill=skin, outline="#d0d0d0", width=2)
        # Hair cap.
        draw.pieslice([cx - head_r - 2, cy_head - head_r - 4, cx + head_r + 2, cy_head + head_r],
                      180, 360, fill=hair)

        # Eyes — blink via openness.
        eye_y = cy_head - int(head_r * 0.15)
        eye_dx = int(head_r * 0.45)
        eye_len = int(head_r * 0.28)
        for sign in (-1, 1):
            ex = fcx + sign * eye_dx
            if eye_open > 0.35:
                draw.ellipse([ex - eye_len, eye_y - eye_len, ex + eye_len, eye_y + eye_len],
                             fill="#ffffff", outline="#1f2937", width=2)
                draw.ellipse([ex - eye_len // 2, eye_y - eye_len // 2, ex + eye_len // 2, eye_y + eye_len // 2],
                             fill="#1f2937")
            else:
                draw.line([ex - eye_len, eye_y, ex + eye_len, eye_y], fill="#1f2937", width=3)

        # Brows.
        brow_y = eye_y - int(head_r * 0.32)
        for sign in (-1, 1):
            bx = fcx + sign * eye_dx
            raise_y = int(brow_y - brow_raise * 8 + (brow_frown * sign * 3))
            draw.line([bx - eye_len, raise_y, bx + eye_len, raise_y + (brow_frown * 6)],
                      fill="#1f2937", width=3)

        # Mouth — openness and curve.
        mouth_y = cy_head + int(head_r * 0.55)
        mw = int(head_r * 0.38)
        mh = max(2, int(head_r * (0.08 + mouth_open * 0.35)))
        curve_off = int(mouth_curve * head_r * 0.5)
        draw.chord([fcx - mw, mouth_y - mh - curve_off, fcx + mw, mouth_y + mh - curve_off],
                   0, 180, fill="#7f2b35", outline="#4a1520")
        if mouth_open > 0.1:
            draw.chord([fcx - mw // 2, mouth_y - mh + int(head_r * 0.04), fcx + mw // 2, mouth_y + mh + int(head_r * 0.06)],
                       0, 180, fill="#5a1a22")

        # Nose hint.
        draw.line([fcx, eye_y + eye_len, fcx, mouth_y - mh - 4], fill="#b08d6a", width=2)

        # Torso + arms from the wardrobe.
        top = clothing["top_color"]
        accent = clothing["accent_color"]
        torso_top = cy_head + head_r + 6
        torso_bottom = int(h * 0.82)
        draw.rounded_rectangle([cx - int(w * 0.28), torso_top, cx + int(w * 0.28), torso_bottom],
                               radius=24, fill=top, outline="#d0d0d0", width=2)
        draw.polygon([(cx - int(w * 0.28), torso_top), (cx + int(w * 0.28), torso_top),
                      (cx + int(w * 0.16), torso_top + int(h * 0.06)), (cx - int(w * 0.16), torso_top + int(h * 0.06))],
                     fill=top)
        # Collar accent.
        draw.line([cx - int(w * 0.06), torso_top, cx, torso_top + int(h * 0.04)], fill=accent, width=4)
        draw.line([cx + int(w * 0.06), torso_top, cx, torso_top + int(h * 0.04)], fill=accent, width=4)

        # Arms: shoulder → elbow → hand, lift controlled by arm params.
        shoulder_y = torso_top + int(h * 0.05)
        for sign, lift in ((-1, arm_left), (1, arm_right)):
            sx = cx + sign * int(w * 0.26)
            ex = sx + sign * int(w * 0.22)
            ey = shoulder_y + int(h * 0.12) - lift * int(h * 0.10)
            hx = ex + sign * int(w * 0.18)
            hy = ey + int(h * 0.16) - lift * int(h * 0.14)
            draw.line([(sx, shoulder_y), (ex, ey)], fill=top, width=14)
            draw.line([(ex, ey), (hx, hy)], fill=top, width=12)
            draw.ellipse([hx - 8, hy - 8, hx + 8, hy + 8], fill=skin)

        # Name plate.
        draw.text((16, 12), f"{actor.name} · {actor.style}/{actor.dimension}",
                  fill="#94a3b8")
        emotion = str(params.get("emotion", "neutral"))
        gesture = str(params.get("gesture", "neutral"))
        draw.text((16, h - 26), f"emotion: {emotion}  gesture: {gesture}",
                  fill="#64748b")

        return np.asarray(img, dtype=np.uint8)


_digital_human: DigitalHumanRenderer | None = None


def get_digital_human() -> DigitalHumanRenderer:
    """Return the shared digital-human renderer singleton."""
    global _digital_human
    if _digital_human is None:
        _digital_human = DigitalHumanRenderer()
    return _digital_human
