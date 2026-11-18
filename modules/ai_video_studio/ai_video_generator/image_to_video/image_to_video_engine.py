"""Image to video engine — real MP4 generation from an image.

If ``source`` points to an existing image file, it is loaded with PIL and
animated with real camera motion (pan / zoom / parallax / handheld) applied
to the actual pixels. When the reference does not exist, a procedural scene
is generated so the pipeline still produces a real video.
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import numpy as np

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.media.canvas import SceneCanvas
from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
from modules.ai_video_studio.media.video import stream_frames_to_video


class ImageToVideoEngine:
    """Runs the real image-to-video pipeline for a job."""

    def generate(self, job: dict[str, Any]) -> dict[str, Any]:
        source = str(job.get("prompt") or job.get("params", {}).get("image_ref") or "").strip()
        if not source:
            raise ValidationError("An image reference is required", field="prompt")
        params = job.get("params", {})
        started = time.time()

        duration = max(1.0, float(params.get("duration", 4.0)))
        fps = max(1, int(params.get("fps", 24)))
        width = int(params.get("width", 1280))
        height = int(params.get("height", 720))
        motion = str(params.get("camera_motion", "parallax")).strip().lower()
        if motion not in self.MOTION_PRESETS:
            raise ValidationError(
                f"Unsupported camera_motion '{motion}'. Choose one of: {', '.join(sorted(self.MOTION_PRESETS))}",
                field="camera_motion",
            )

        total = max(1, int(round(duration * fps)))
        out = unique_filename(get_subsystem_dir("videos"), "image_to_video", "mp4")
        video_result = stream_frames_to_video(
            self._iter_frames(source, motion, total, fps, width, height),
            out, fps=fps, total_frames=total, require_mp4=True,
        )

        return {
            "mode": "image_to_video",
            "source": source,
            "image_loaded": bool(Path(source).is_file()),
            "camera_motion": motion,
            "frames": video_result["frames"],
            "fps": fps,
            "duration": duration,
            "output_path": video_result["output_path"],
            "output_bytes": video_result["bytes"],
            "encode_engine": video_result["engine"],
            "elapsed_seconds": round(time.time() - started, 3),
            "output_ref": f"itv_{job.get('id')}",
        }

    MOTION_PRESETS = {
        "parallax", "zoom", "push_in", "pull_out", "pan", "pan_left",
        "pan_right", "tilt_up", "tilt_down", "orbit", "handheld",
    }

    # ── Frame production ──────────────────────────────────────────
    def _iter_frames(
        self, source: str, motion: str, total: int, fps: int, width: int, height: int,
    ):
        """Yield frames lazily so a long sequence does not fill RAM."""
        from PIL import Image

        try:
            with Image.open(source) as opened:
                base = opened.convert("RGB")
        except Exception:  # noqa: BLE001 — missing/unreadable source → procedural
            scene = self._procedural_scene(source, motion, width, height)
            canvas = SceneCanvas(width=width, height=height, fps=fps)
            for index in range(total):
                yield canvas.render_scene(scene, index)
            return

        # Cover the output canvas once; motion crops are then taken from this
        # overscanned image to avoid black borders during pans and rotation.
        scale = max(width / base.width, height / base.height) * 1.24
        base = base.resize((max(width + 2, int(base.width * scale)), max(height + 2, int(base.height * scale))), Image.Resampling.LANCZOS)
        for index in range(total):
            t = index / max(1, total - 1)
            yield self._animate_pixels(base, motion, t, width, height)

    def _render_frames(
        self, source: str, motion: str, total: int, fps: int, width: int, height: int,
    ) -> list[np.ndarray]:
        try:
            from PIL import Image

            base = Image.open(source).convert("RGB")
        except Exception:  # noqa: BLE001 — missing/unreadable source → procedural
            scene = self._procedural_scene(source, motion, width, height)
            canvas = SceneCanvas(width=width, height=height, fps=fps)
            return [canvas.render_scene(scene, i) for i in range(total)]

        base = base.resize((width, height), Image.BILINEAR)
        frames: list[np.ndarray] = []
        for i in range(total):
            t = i / max(1, total - 1)
            frames.append(self._animate_pixels(base, motion, t, width, height))
        return frames

    def _animate_pixels(
        self, base: Any, motion: str, t: float, width: int, height: int,
    ) -> np.ndarray:
        """Apply eased cinematic camera movement to the source image."""
        from PIL import Image
        import math

        eased = t * t * (3.0 - 2.0 * t)
        alias = {"zoom": "push_in", "pan": "pan_right"}.get(motion, motion)
        zoom_delta = {
            "push_in": 0.16, "pull_out": -0.10, "parallax": 0.075,
            "pan_left": 0.025, "pan_right": 0.025,
            "tilt_up": 0.02, "tilt_down": 0.02, "orbit": 0.055,
            "handheld": 0.035,
        }.get(alias, 0.0)
        zoom = 1.0 + zoom_delta * eased
        nw = max(width + 1, int(base.width * zoom))
        nh = max(height + 1, int(base.height * zoom))
        img = base.resize((nw, nh), Image.Resampling.BICUBIC)

        max_x = max(0, nw - width)
        max_y = max(0, nh - height)
        center_x = max_x / 2.0
        center_y = max_y / 2.0
        dx = dy = 0.0
        if alias in {"pan_left", "parallax"}:
            dx = -max_x * 0.42 * eased
        elif alias == "pan_right":
            dx = max_x * 0.42 * eased
        elif alias == "tilt_up":
            dy = -max_y * 0.42 * eased
        elif alias == "tilt_down":
            dy = max_y * 0.42 * eased
        elif alias == "orbit":
            dx = max_x * 0.18 * math.sin(eased * math.pi)
            dy = -max_y * 0.12 * math.sin(eased * math.pi)
            img = img.rotate(1.8 * math.sin(eased * math.pi), resample=Image.Resampling.BICUBIC)
        elif alias == "handheld":
            dx = math.sin(t * 2 * math.pi * 2.7) * width * 0.006
            dy = math.cos(t * 2 * math.pi * 2.1) * height * 0.005

        left = int(max(0, min(max_x, center_x + dx)))
        top = int(max(0, min(max_y, center_y + dy)))
        frame = img.crop((left, top, left + width, top + height))
        return np.asarray(frame, dtype=np.uint8)

    def _procedural_scene(self, source: str, motion: str, width: int, height: int) -> dict[str, Any]:
        """Fallback scene used when the source image cannot be loaded."""
        from modules.ai_video_studio.ai_video_generator.image_to_video.image_parser import ImageParser

        parsed = ImageParser().parse(source)
        camera = {"dx": 0.4, "dy": 0.0, "zoom": 1.0, "roll": 0.0}
        if motion in {"zoom", "push_in"}:
            camera = {"dx": 0.0, "dy": 0.0, "zoom": 1.16, "roll": 0.0}
        elif motion == "pull_out":
            camera = {"dx": 0.0, "dy": 0.0, "zoom": 0.90, "roll": 0.0}
        elif motion in {"pan", "pan_right"}:
            camera = {"dx": 0.8, "dy": 0.0, "zoom": 1.0, "roll": 0.0}
        elif motion == "pan_left":
            camera = {"dx": -0.8, "dy": 0.0, "zoom": 1.0, "roll": 0.0}
        elif motion == "tilt_up":
            camera = {"dx": 0.0, "dy": -0.7, "zoom": 1.0, "roll": 0.0}
        elif motion == "tilt_down":
            camera = {"dx": 0.0, "dy": 0.7, "zoom": 1.0, "roll": 0.0}
        elif motion == "orbit":
            camera = {"dx": 0.25, "dy": -0.2, "zoom": 1.055, "roll": 0.025}
        return {
            "background_type": "gradient",
            "background_colors": ["#1a1a2e", "#16213e", "#0f3460"],
            "name": source,
            "image_ref": parsed["ref"],
            "particles": [
                {"x": (k * 173) % width, "y": -8.0, "vx": -0.3, "vy": 1.0 + (k % 3) * 0.4,
                 "radius": 2, "color": "#FFFFFF"}
                for k in range(12)
            ],
            "circles": [
                {"x": width * 0.75, "y": height * 0.3, "radius": 90, "color": "#facc1577", "dx": -0.2, "dy": 0.05},
                {"x": width * 0.25, "y": height * 0.65, "radius": 60, "color": "#7dd3fc66", "dx": 0.15, "dy": -0.05},
            ],
            "rects": [
                {"x": 80, "y": height * 0.7, "w": 260, "h": 120, "color": "#334155", "dx": 0.2},
                {"x": width - 340, "y": height * 0.72, "w": 240, "h": 100, "color": "#334155", "dx": -0.15},
            ],
            "camera": camera,
            "palette": ["#1a1a2e", "#0f3460", "#e94560"],
            "noise": 0.05,
        }
