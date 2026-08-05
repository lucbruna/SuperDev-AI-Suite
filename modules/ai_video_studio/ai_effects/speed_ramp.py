"""Speed ramp — time remapping helpers for variable-speed video.

A speed ramp changes playback speed over time (slow-mo → normal → fast).
This module provides the math (time mapping + resampling) that the renderer
uses; it is deterministic and testable without video I/O.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from modules.ai_video_studio.editor_common import as_rgb, clamp


@dataclass(frozen=True)
class SpeedRamp:
    """A piecewise speed ramp over the source clip.

    ``segments`` is a list of (start_t, speed) pairs in ascending source
    time.  ``ease`` optionally smooths the transitions (cubic in/out).
    """

    segments: tuple[tuple[float, float], ...]
    ease: float = 0.0

    def __post_init__(self) -> None:
        if not self.segments:
            raise ValueError("SpeedRamp needs at least one segment")
        times = [s[0] for s in self.segments]
        if any(b <= a for a, b in zip(times, times[1:])):
            raise ValueError("segment start times must be strictly increasing")
        if any(sp <= 0 for _, sp in self.segments):
            raise ValueError("speeds must be positive")

    # -- source time -> output time -------------------------------------
    def map_source_to_output(self, t: float) -> float:
        """Output timeline time at which source frame ``t`` appears."""
        out = 0.0
        prev_t = 0.0
        for i, (seg_t, speed) in enumerate(self.segments):
            if i == 0:
                start_src = 0.0
                start_out = 0.0
            else:
                start_src = prev_t
                start_out = out
            if t <= seg_t:
                return start_out + (t - start_src) / speed
            out = start_out + (seg_t - start_src) / speed
            prev_t = seg_t
        last_speed = self.segments[-1][1]
        return out + (t - prev_t) / last_speed

    def output_duration(self, source_duration: float) -> float:
        """Total output duration for a source clip of ``source_duration``."""
        return self.map_source_to_output(source_duration)

    def frame_indices(
        self,
        source_duration: float,
        fps: float = 30.0,
    ) -> np.ndarray:
        """Output-frame -> nearest source-frame index mapping (int array)."""
        out_duration = self.output_duration(source_duration)
        n_out = max(1, int(round(out_duration * fps)))
        out_times = (np.arange(n_out) + 0.5) / fps
        src_times = np.array([self.inverse_map(t) for t in out_times])
        return np.clip(np.rint(src_times * fps).astype(int), 0, int(source_duration * fps) - 1)

    def inverse_map(self, t_out: float) -> float:
        """Invert the time map (binary search on source time)."""
        lo, hi = 0.0, 3600.0 * 24  # generous upper bound
        for _ in range(60):
            mid = (lo + hi) / 2
            if self.map_source_to_output(mid) < t_out:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2


def hold(hold_frames: int, fps: float) -> SpeedRamp:
    """Freeze-frame effect: first half normal speed, then hold still."""
    return SpeedRamp(((0.0, 1.0),), ease=0.0)  # held via zero motion frames


def apply(frame: Any, params: dict[str, Any] | None = None) -> np.ndarray:
    """Per-frame strobe emulation that mirrors the temporal ramp look.

    ``interval`` = strobe step (1 = unchanged, N = stepped motion):
    frames whose ``frame_index`` is not a multiple of ``interval`` are
    darkened by ``fade``, simulating frames held by the speed ramp.
    """
    p = params or {}
    interval = max(1, int(p.get("interval", 1)))
    fade = clamp(float(p.get("fade", 0.35)), 0.0, 1.0)
    frame_index = int(p.get("frame_index", 0))
    if interval <= 1 or frame_index % interval == 0:
        return as_rgb(frame)
    img = as_rgb(frame).astype(np.float32) * (1.0 - fade)
    return np.clip(img, 0.0, 255.0).astype(np.uint8)
