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
from modules.ai_video_studio.media.video import frames_to_video


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
        motion = params.get("camera_motion", "parallax")

        total = max(1, int(duration * fps))
        frames = self._render_frames(source, motion, total, fps, width, height)

        out = unique_filename(get_subsystem_dir("videos"), "image_to_video", "mp4")
        video_result = frames_to_video(frames, out, fps=fps)

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

    # ── Frame production ──────────────────────────────────────────
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
        """Apply camera motion to the actual image pixels."""
        from PIL import Image

        if motion == "zoom":
            zoom = 1.0 + 0.15 * t
            nw = max(width + 1, int(width * zoom))
            nh = max(height + 1, int(height * zoom))
            img = base.resize((nw, nh), Image.BILINEAR).crop(
                ((nw - width) // 2, (nh - height) // 2,
                 (nw - width) // 2 + width, (nh - height) // 2 + height)
            )
        elif motion == "pan":
            dx = int(0.15 * width * t)
            img = base.transform(base.size, Image.AFFINE, (1, 0, dx, 0, 1, 0), resample=Image.BILINEAR, fillcolor=0)
        elif motion == "parallax":
            # Slight zoom-in + horizontal drift reads as depth movement.
            zoom = 1.0 + 0.08 * t
            nw = max(width + 1, int(width * zoom))
            nh = max(height + 1, int(height * zoom))
            dx = int(0.04 * width * t)
            img = base.resize((nw, nh), Image.BILINEAR)
            img = img.crop((dx, (nh - height) // 2, dx + width, (nh - height) // 2 + height))
        else:  # handheld — subtle shake
            import math

            dx = int(math.sin(t * 40) * 4)
            dy = int(math.cos(t * 31) * 3)
            img = base.transform(base.size, Image.AFFINE, (1, 0, dx, 0, 1, dy), resample=Image.BILINEAR, fillcolor=0)
        return np.asarray(img, dtype=np.uint8)

    def _procedural_scene(self, source: str, motion: str, width: int, height: int) -> dict[str, Any]:
        """Fallback scene used when the source image cannot be loaded."""
        from modules.ai_video_studio.ai_video_generator.image_to_video.image_parser import ImageParser

        parsed = ImageParser().parse(source)
        camera = {"dx": 0.4, "dy": 0.0, "zoom": 1.0, "roll": 0.0}
        if motion == "zoom":
            camera = {"dx": 0.0, "dy": 0.0, "zoom": 1.15, "roll": 0.0}
        elif motion == "pan":
            camera = {"dx": 0.8, "dy": 0.0, "zoom": 1.0, "roll": 0.0}
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
