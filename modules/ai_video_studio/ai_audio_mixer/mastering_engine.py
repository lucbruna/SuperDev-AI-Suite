"""Mastering Engine — a real mastering chain for mixed audio."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import dsp
from modules.ai_video_studio.ai_audio_mixer.equalizer import tone_controls, apply_preset
from modules.ai_video_studio.ai_audio_mixer.compressor import compress
from modules.ai_video_studio.ai_audio_mixer.limiter import limit
from modules.ai_video_studio.ai_audio_mixer.loudness_normalizer import normalize, estimate_loudness


class MasteringEngine:
    """Applies the classic master bus chain."""

    def master(self, x: np.ndarray, *, preset: str = "flat", bass_db: float = 0.0,
               mid_db: float = 0.0, treble_db: float = 0.0,
               threshold_db: float = -16.0, ratio: float = 2.5,
               target_rms: float = 0.24, sample_rate: int = dsp.SAMPLE_RATE) -> dict:
        """Master a mix; returns processed audio + loudness report."""
        out = x.astype(np.float32)
        out = apply_preset(out, preset, sample_rate=sample_rate)
        out = tone_controls(out, bass_db=bass_db, mid_db=mid_db, treble_db=treble_db,
                            sample_rate=sample_rate)
        out = compress(out, threshold_db=threshold_db, ratio=ratio, makeup_db=1.0,
                       sample_rate=sample_rate)
        out = limit(out, threshold=0.97, sample_rate=sample_rate)
        out = normalize(out, target_rms=target_rms, target_peak=0.95, sample_rate=sample_rate)
        return {"samples": out, "loudness": estimate_loudness(out, sample_rate=sample_rate)}


def master(x: np.ndarray, **kwargs) -> np.ndarray:
    return MasteringEngine().master(x, **kwargs)["samples"]
