"""Old movie restoration — film-era damage recovery (flicker, scratches,
dirt, dust, grain) applied frame-by-frame with deterministic behavior.

All frames are float arrays in [0, 1]; helper functions come from the
other ai_restoration modules.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.ai_restoration.denoise_video import denoise
from modules.ai_video_studio.ai_restoration.scratch_removal import remove_scratches
from modules.ai_video_studio.ai_restoration.dust_removal import remove_dust
from modules.ai_video_studio.ai_restoration.color_restoration import restore_color


class OldMovieRestoration:
    """Restores vintage film: flicker → scratches → dirt → denoise → grade."""

    def __init__(
        self,
        *,
        flicker_window: int = 9,
        scratch_threshold: float = 0.5,
        dust_sensitivity: float = 0.25,
        denoise_strength: float = 0.5,
    ) -> None:
        self._flicker_window = max(5, int(flicker_window) | 1)
        self._scratch_threshold = float(scratch_threshold)
        self._dust_sensitivity = float(dust_sensitivity)
        self._denoise_strength = float(denoise_strength)
        self._stats: dict[str, Any] = {}

    # ── Public API ─────────────────────────────────────────────
    def restore(
        self, frames: list[np.ndarray], *, fix_flicker: bool = True, denoise_frames: bool = True
    ) -> list[np.ndarray]:
        """Restore a sequence of old-movie frames (float [0, 1])."""
        if not frames:
            raise ValidationError("restore: no frames provided")
        if any(f is None for f in frames):
            raise ValidationError("restore: missing frames must be pre-filled")
        ref = next(f for f in frames if f is not None)
        if ref.ndim != 3:
            raise ValidationError("restore: frames must be HxWxC arrays")

        work = [f.copy() for f in frames]
        stats: dict[str, Any] = {"flicker": 0, "scratch": 0, "dirt": 0, "denoise": 0}

        if fix_flicker:
            work = self._fix_flicker(work)
            stats["flicker"] = len(work)

        for i, frame in enumerate(work):
            # Vertical scratches (typical of old prints)
            cleaned = remove_scratches(frame, threshold=self._scratch_threshold)
            if not np.array_equal(cleaned, frame):
                work[i] = cleaned
                stats["scratch"] += 1
            # Dirt/dust specks
            cleaned = remove_dust(work[i], sensitivity=self._dust_sensitivity)
            if not np.array_equal(cleaned, work[i]):
                work[i] = cleaned
                stats["dirt"] += 1

        if denoise_frames:
            work = [denoise(f, strength=self._denoise_strength) for f in work]
            stats["denoise"] = len(work)

        # Warm grade + fade compensation typical of restored vintage film
        work = [restore_color(f) for f in work]

        self._stats = stats
        return work

    def restore_frame(
        self, frame: np.ndarray, neighbors: list[np.ndarray] | None = None
    ) -> np.ndarray:
        """Restore a single frame (float [0, 1]); neighbors are unused but
        accepted for API parity with other repair engines."""
        if frame.ndim != 3:
            raise ValidationError("restore_frame: frame must be HxWxC")
        out = remove_scratches(frame, threshold=self._scratch_threshold)
        out = remove_dust(out, sensitivity=self._dust_sensitivity)
        out = denoise(out, strength=self._denoise_strength)
        return restore_color(out)

    def stats(self) -> dict[str, Any]:
        return dict(self._stats)

    # ── Internals ──────────────────────────────────────────────
    def _fix_flicker(self, frames: list[np.ndarray]) -> list[np.ndarray]:
        """Normalize per-frame mean luma to the sequence trend (rolling window)."""
        means = np.array([f.mean() for f in frames], dtype=np.float64)
        n = len(means)
        # Rolling window mean (truncated at the edges) — the flicker trend
        target = np.zeros(n, dtype=np.float64)
        kernel = self._flicker_window // 2
        for i in range(n):
            lo = max(0, i - kernel)
            hi = min(n, i + kernel + 1)
            target[i] = means[lo:hi].mean()

        gain = (target / (means + 1e-6)).clip(0.5, 2.0)
        return [
            np.clip(f * gain[i], 0.0, 1.0) for i, f in enumerate(frames)
        ]


old_movie_restoration = OldMovieRestoration()
