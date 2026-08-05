"""Camera tracking — estimate global camera motion between consecutive frames."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


class CameraTracker:
    """Phase-correlation camera motion estimator.

    Computes the dominant translation between two frames via the FFT
    phase correlation peak.
    """

    def estimate(self, a: NDArray[np.floating], b: NDArray[np.floating]) -> dict[str, float]:
        fa = a.mean(axis=-1).astype(np.float64)
        fb = b.mean(axis=-1).astype(np.float64)
        h, w = fa.shape
        if fa.shape != fb.shape:
            raise ValueError("frames must have the same shape")
        # Hanning window to reduce edge artifacts
        win = np.outer(np.hanning(h), np.hanning(w))
        fft_a = np.fft.fft2(fa * win)
        fft_b = np.fft.fft2(fb * win)
        cross = fft_a * np.conj(fft_b)
        pcorr = np.abs(np.fft.ifft2(cross / (np.abs(cross) + 1e-8)))
        dy, dx = np.unravel_index(np.argmax(pcorr), (h, w))
        if dy > h // 2:
            dy -= h
        if dx > w // 2:
            dx -= w
        confidence = float(pcorr.max())
        return {"dx": float(dx), "dy": float(dy), "confidence": confidence}

    def track(self, frames: list[NDArray[np.floating]]) -> list[dict[str, float]]:
        out = []
        for a, b in zip(frames, frames[1:], strict=False):
            out.append(self.estimate(a, b))
        return out
