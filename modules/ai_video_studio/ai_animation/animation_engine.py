"""Animation engine — render character animation into real videos.

Composes motion (walk/run/jump/idle), skeletal pose and facial data into
frames drawn with PIL (a stylized skeleton character), then encodes them
into a real MP4 under ``modules/downloads/animations/``.
"""
from __future__ import annotations

import math
import time
from typing import Any

import numpy as np

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
from modules.ai_video_studio.media.render import render_sim_frames


class AnimationEngine:
    """Runs real animation render jobs."""

    _ACTIONS = {"idle", "walk", "run", "jump", "wave", "sit"}

    def __init__(self) -> None:
        self._jobs: dict[str, dict[str, Any]] = {}

    def animate(
        self,
        *,
        character: str = "default",
        action: str = "walk",
        duration: float = 3.0,
        fps: int = 24,
        facial: dict[str, Any] | None = None,
        job_id: str | None = None,
    ) -> dict[str, Any]:
        if duration <= 0:
            raise ValidationError("duration must be positive", field="duration")
        if action not in self._ACTIONS:
            action = "idle"

        rid = job_id or f"anim_{len(self._jobs) + 1}"
        started = time.time()
        total_frames = max(1, int(duration * fps))

        frames: list[np.ndarray] = []
        for i in range(total_frames):
            t = i / max(1, total_frames - 1)
            frames.append(self._render_frame(character, action, t, fps=fps))

        out = unique_filename(get_subsystem_dir("animations"), f"{action}_{character}", "mp4")
        video_result = render_sim_frames(
            lambda i: frames[i], out, frames=total_frames, fps=fps,
        )

        result = {
            "id": rid,
            "character": character,
            "action": action,
            "duration": duration,
            "fps": fps,
            "total_frames": total_frames,
            "output_path": video_result["output_path"],
            "output_bytes": video_result["bytes"],
            "encode_engine": video_result["engine"],
            "elapsed_seconds": round(time.time() - started, 3),
            "status": "ok",
        }
        self._jobs[rid] = result
        return result

    def get(self, job_id: str) -> dict[str, Any] | None:
        return dict(self._jobs[job_id]) if job_id in self._jobs else None

    def list_jobs(self) -> list[str]:
        return list(self._jobs.keys())

    # ── Frame rendering (PIL skeleton) ────────────────────────────
    def _render_frame(self, character: str, action: str, t: float, *, fps: int) -> np.ndarray:
        from PIL import Image, ImageDraw

        w, h = 640, 360
        img = Image.new("RGB", (w, h), "#0f172a")
        draw = ImageDraw.Draw(img)

        # Ground line.
        ground = h - 40
        draw.line([40, ground, w - 40, ground], fill="#334155", width=2)

        phase = t * math.pi * 2
        amp = {"walk": 1.0, "run": 1.6, "idle": 0.15, "jump": 0.0, "wave": 0.3, "sit": 0.0}[action]

        # Body positions.
        cx = w / 2
        if action == "jump":
            bounce = 4 * t * (1 - t)  # parabola
            cy = ground - 150 * (1 + bounce)
        else:
            cy = ground - 140

        # Head bob from stride.
        bob = math.sin(phase) * 6 * amp if action in ("walk", "run") else math.sin(t * 6) * 1.5

        head = (cx, cy - 40 + bob)
        hip = (cx, cy + 55 + bob)
        neck = (cx, cy - 15 + bob)

        # Legs.
        swing = math.sin(phase) * 30 * amp if action in ("walk", "run") else 0
        foot_l = (cx - 25 + swing, ground)
        foot_r = (cx + 25 - swing, ground)
        knee_l = ((hip[0] - 12 + swing * 0.5), (hip[1] + foot_l[1]) / 2 + 10)
        knee_r = ((hip[0] + 12 - swing * 0.5), (hip[1] + foot_r[1]) / 2 + 10)

        # Arms.
        if action == "wave":
            arm_angle = math.sin(t * 8) * 30
            hand_l = (cx - 45, cy - 55 + math.sin(arm_angle) * 20)
            elbow_l = (cx - 30, cy - 25)
        else:
            arm_swing = math.sin(phase + math.pi) * 25 * amp
            hand_l = (cx - 40 + arm_swing, cy - 20)
            elbow_l = (cx - 22 + arm_swing * 0.6, cy - 5)
        hand_r = (cx + 40 - swing, cy - 15)
        elbow_r = (cx + 22 - swing * 0.6, cy - 5)

        # Draw skeleton as thick lines (bones) + joint circles.
        bone_color = "#e2e8f0"
        joint_color = "#38bdf8"
        for a, b in [
            (neck, hip),              # spine
            (hip, knee_l), (knee_l, foot_l),   # left leg
            (hip, knee_r), (knee_r, foot_r),   # right leg
            (neck, elbow_l), (elbow_l, hand_l),  # left arm
            (neck, elbow_r), (elbow_r, hand_r),  # right arm
            (head, neck),
        ]:
            draw.line([a, b], fill=bone_color, width=6)

        # Head.
        head_r = 18
        draw.ellipse([head[0] - head_r, head[1] - head_r, head[0] + head_r, head[1] + head_r], fill="#94a3b8", outline=bone_color, width=3)
        # Eyes (simple facial expression).
        eye_offset = 6
        draw.ellipse([head[0] - eye_offset - 3, head[1] - 4, head[0] - eye_offset + 3, head[1] + 2], fill="#0f172a")
        draw.ellipse([head[0] + eye_offset - 3, head[1] - 4, head[0] + eye_offset + 3, head[1] + 2], fill="#0f172a")

        # Joints.
        for joint in [neck, hip, knee_l, knee_r, elbow_l, elbow_r]:
            draw.ellipse([joint[0] - 4, joint[1] - 4, joint[0] + 4, joint[1] + 4], fill=joint_color)

        # Label.
        draw.text((20, 16), f"{character} — {action}  [{round(t, 2)}]", fill="#94a3b8")

        return np.asarray(img, dtype=np.uint8)


_animation_engine: AnimationEngine | None = None


def get_animation_engine() -> AnimationEngine:
    global _animation_engine
    if _animation_engine is None:
        _animation_engine = AnimationEngine()
    return _animation_engine
