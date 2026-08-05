"""Physics engine — orchestrate physics simulations for scenes."""
from __future__ import annotations

import time
from typing import Any

import numpy as np

from modules.ai_video_studio.core.exceptions import ValidationError


class PhysicsEngine:
    """Runs deterministic physics steps for scene bodies and effects."""

    def __init__(self, *, gravity: float = 9.81, substeps: int = 4) -> None:
        self.gravity = gravity
        self.substeps = substeps
        self._bodies: list[dict[str, Any]] = []

    def add_body(self, *, name: str, mass: float = 1.0, position: tuple[float, float, float] = (0, 0, 0)) -> str:
        if mass <= 0:
            raise ValidationError("mass must be positive", field="mass")
        body = {
            "id": name,
            "mass": mass,
            "position": list(position),
            "velocity": [0.0, 0.0, 0.0],
        }
        self._bodies.append(body)
        return name

    def step(self, dt: float = 1 / 60) -> list[dict[str, Any]]:
        if dt <= 0:
            raise ValidationError("dt must be positive", field="dt")
        sub_dt = dt / self.substeps
        for body in self._bodies:
            body["velocity"][1] -= self.gravity * sub_dt  # gravity on Y
            for axis in range(3):
                body["position"][axis] += body["velocity"][axis] * sub_dt
        return [dict(b) for b in self._bodies]

    def bodies(self) -> list[dict[str, Any]]:
        return [dict(b) for b in self._bodies]

    def reset(self) -> None:
        self._bodies.clear()

    # ── Real output ───────────────────────────────────────────────
    def render_simulation(self, *, duration: float = 4.0, fps: int = 24, seed: int = 7) -> dict[str, Any]:
        """Render a real particle-physics video.

        Simulates falling particles with gravity and bounces off the ground,
        drawing them with PIL. Output: ``modules/downloads/physics/``.
        """
        import random

        from PIL import Image, ImageDraw

        from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
        from modules.ai_video_studio.media.render import render_sim_frames

        started = time.time()
        w, h = 640, 360
        ground = h - 40
        rng = random.Random(seed)

        particles = [
            {
                "x": rng.uniform(40, w - 40),
                "y": rng.uniform(-60, -10),
                "vx": rng.uniform(-30, 30),
                "vy": 0.0,
                "r": rng.uniform(3, 9),
                "color": rng.choice(["#f472b6", "#38bdf8", "#fbbf24", "#34d399", "#a78bfa"]),
            }
            for _ in range(40)
        ]
        total = max(1, int(duration * fps))

        def _make_frame(i: int) -> np.ndarray:
            img = Image.new("RGB", (w, h), "#0b1220")
            draw = ImageDraw.Draw(img)
            draw.line([40, ground, w - 40, ground], fill="#334155", width=2)
            dt = 1 / fps
            for p in particles:
                p["vy"] += self.gravity * 30 * dt
                p["x"] += p["vx"] * dt
                p["y"] += p["vy"] * dt
                if p["y"] > ground - p["r"]:
                    p["y"] = ground - p["r"]
                    p["vy"] *= -0.55
                    p["vx"] *= 0.98
                draw.ellipse(
                    [p["x"] - p["r"], p["y"] - p["r"], p["x"] + p["r"], p["y"] + p["r"]],
                    fill=p["color"],
                )
            draw.text((16, 16), f"physics  gravity={self.gravity}  frame={i}", fill="#94a3b8")
            return np.asarray(img, dtype=np.uint8)

        out = unique_filename(get_subsystem_dir("physics"), "particles", "mp4")
        video_result = render_sim_frames(_make_frame, out, frames=total, fps=fps)
        return {
            "particles": len(particles),
            "gravity": self.gravity,
            "output_path": video_result["output_path"],
            "output_bytes": video_result["bytes"],
            "encode_engine": video_result["engine"],
            "elapsed_seconds": round(time.time() - started, 3),
        }


_physics_engine: PhysicsEngine | None = None


def get_physics_engine() -> PhysicsEngine:
    """Cached singleton physics engine."""
    global _physics_engine
    if _physics_engine is None:
        _physics_engine = PhysicsEngine()
    return _physics_engine
