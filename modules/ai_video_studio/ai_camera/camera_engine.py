"""Camera engine — orchestrate virtual camera behaviour."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_camera.virtual_camera import VirtualCamera


class CameraEngine:
    """Creates and manages virtual cameras with paths and behaviours."""

    def __init__(self) -> None:
        self._cameras: dict[str, VirtualCamera] = {}
        self._active: str | None = None

    def create(self, name: str, **kwargs: Any) -> VirtualCamera:
        if name in self._cameras:
            raise ValueError(f"Camera '{name}' already exists")
        camera = VirtualCamera(**kwargs)
        self._cameras[name] = camera
        if self._active is None:
            self._active = name
        return camera

    def active_camera(self) -> VirtualCamera:
        if self._active is None:
            raise ValueError("No camera created yet")
        return self._cameras[self._active]

    def set_active(self, name: str) -> None:
        if name not in self._cameras:
            raise ValueError(f"Camera '{name}' not found")
        self._active = name

    def list_cameras(self) -> list[str]:
        return list(self._cameras.keys())

    # ── Real output ───────────────────────────────────────────────
    def render_demo(self, *, camera_name: str | None = None, move: str = "orbit", duration: float = 4.0, fps: int = 24) -> dict[str, Any]:
        """Render a real video demonstrating a camera move.

        The video shows a 3D grid of points viewed through the camera, with
        the requested cinematic move applied over time. The file is written
        to ``modules/downloads/camera/``.
        """
        import time

        import numpy as np

        from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
        from modules.ai_video_studio.media.render import render_sim_frames

        started = time.time()
        total = max(1, int(duration * fps))
        name = camera_name or self._active or "cam_0"

        def _make_frame(i: int) -> np.ndarray:
            from PIL import Image, ImageDraw

            w, h = 640, 360
            t = i / max(1, total - 1)
            img = Image.new("RGB", (w, h), "#0b1220")
            draw = ImageDraw.Draw(img)

            # Grid of "world" points.
            points = []
            for gx in range(-3, 4):
                for gz in range(1, 7):
                    points.append((w / 2 + gx * 40, h / 2 + 40 / gz - 40, gz))

            # Camera offset from move type.
            import math

            if move == "orbit":
                dx = math.sin(t * math.pi * 2) * 140
                dy = math.cos(t * math.pi * 2) * 40
                zoom = 1.0
            elif move == "dolly_in":
                dx, dy, zoom = 0.0, 0.0, 0.5 + 0.5 * (1 - t)
            elif move == "crane_up":
                dx, dy, zoom = 0.0, -80 * t, 1.0
            elif move == "handheld":
                dx = math.sin(i * 0.9) * 6
                dy = math.cos(i * 1.3) * 5
                zoom = 1.0
            else:  # pan
                dx = -160 * t
                dy = 0.0
                zoom = 1.0

            for (px, py, depth) in points:
                sx = (px + dx) * zoom
                sy = (py + dy) * zoom
                size = max(2, int(6 / depth * 10))
                color = "#f472b6" if depth % 2 else "#38bdf8"
                draw.ellipse([sx - size, sy - size, sx + size, sy + size], fill=color)

            draw.text((16, 16), f"camera={name}  move={move}  t={round(t, 2)}", fill="#94a3b8")
            return np.asarray(img, dtype=np.uint8)

        out = unique_filename(get_subsystem_dir("camera"), f"{move}", "mp4")
        video_result = render_sim_frames(_make_frame, out, frames=total, fps=fps)
        return {
            "camera": name,
            "move": move,
            "output_path": video_result["output_path"],
            "output_bytes": video_result["bytes"],
            "encode_engine": video_result["engine"],
            "elapsed_seconds": round(time.time() - started, 3),
        }


_camera_engine: CameraEngine | None = None


def get_camera_engine() -> CameraEngine:
    """Cached singleton camera engine."""
    global _camera_engine
    if _camera_engine is None:
        _camera_engine = CameraEngine()
    return _camera_engine
