"""Generation optimizer — tune generation parameters for speed/quality."""

from __future__ import annotations

from typing import Any

# Defaults per output resolution — (width, height, steps)
_RESOLUTION_STEPS = {
    "480p": (854, 480, 20),
    "720p": (1280, 720, 25),
    "1080p": (1920, 1080, 30),
    "4k": (3840, 2160, 40),
}


class GenerationOptimizer:
    """Computes optimal parameter sets given a target resolution and speed."""

    def __init__(self) -> None:
        self._profiles: dict[str, dict[str, Any]] = {
            "speed": {"steps_scale": 0.7, "guidance_scale": 4.0},
            "balanced": {"steps_scale": 1.0, "guidance_scale": 7.0},
            "quality": {"steps_scale": 1.4, "guidance_scale": 9.0},
        }

    def optimize(
        self,
        *,
        resolution: str = "720p",
        profile: str = "balanced",
        fps: int = 24,
        duration: float = 5.0,
    ) -> dict[str, Any]:
        if resolution not in _RESOLUTION_STEPS:
            raise ValueError(f"Unknown resolution '{resolution}'")
        if profile not in self._profiles:
            raise ValueError(f"Unknown profile '{profile}'")
        width, height, base_steps = _RESOLUTION_STEPS[resolution]
        prof = self._profiles[profile]
        steps = max(4, int(base_steps * prof["steps_scale"]))
        total_frames = max(1, int(duration * fps))
        return {
            "width": width,
            "height": height,
            "fps": fps,
            "duration": duration,
            "steps": steps,
            "guidance_scale": prof["guidance_scale"],
            "total_frames": total_frames,
            "profile": profile,
        }

    def estimate_runtime(self, params: dict[str, Any]) -> float:
        """Rough seconds estimate based on resolution and steps."""
        width = params.get("width", 1280)
        height = params.get("height", 720)
        steps = params.get("steps", 25)
        frames = params.get("total_frames", 120)
        per_frame = (width * height) / (1280 * 720) * steps * 0.02
        return round(frames * per_frame, 2)

    def add_profile(self, name: str, config: dict[str, Any]) -> None:
        self._profiles[name] = config


_generation_optimizer: GenerationOptimizer | None = None


def get_generation_optimizer() -> GenerationOptimizer:
    global _generation_optimizer
    if _generation_optimizer is None:
        _generation_optimizer = GenerationOptimizer()
    return _generation_optimizer
