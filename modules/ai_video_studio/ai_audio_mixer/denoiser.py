"""Denoiser — practical noise reduction for audio tracks."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp


def denoise(x: np.ndarray, *, threshold: float = 0.015, amount: float = 1.0,
            sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    """Spectral-gate noise reduction blended by ``amount`` (0-1)."""
    if amount <= 0:
        return x.copy()
    cleaned = dsp.spectral_gate(x, threshold=threshold, sample_rate=sample_rate)
    return ((1 - amount) * x + amount * cleaned).astype(np.float32)


def noise_reduce(x: np.ndarray, *, noise_profile: np.ndarray | None = None,
                 sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    """Subtract a stationary noise profile in the spectral domain.

    ``noise_profile`` is a magnitude spectrum; when omitted a quiet-tail
    estimate is used.
    """
    n = len(x)
    fft_size = min(2048, n if n > 0 else 1)
    if n < fft_size:
        return x.copy()
    if noise_profile is None:
        tail = x[-fft_size:]
        noise_profile = np.abs(np.fft.rfft(tail)) + 1e-9
    spec = np.fft.rfft(x[:fft_size])
    mag = np.abs(spec)
    cleaned = np.maximum(mag - noise_profile[: len(mag)] * 1.2, 0.0)
    spec_clean = cleaned * np.exp(1j * np.angle(spec))
    out = np.fft.irfft(spec_clean, fft_size)
    return dsp.normalize_peak(out, dsp.peak(x) + 1e-9).astype(np.float32)
