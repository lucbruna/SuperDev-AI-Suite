"""Speaker Encoder — builds a compact fixed-size voice embedding.

Without a deep speaker-encoder model on CPU, the embedding is a normalized
feature vector of measurable acoustic properties: pitch statistics, spectral
balance and energy. Two embeddings of the same speaker are much closer
(cosine) than embeddings of different speakers.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.media import dsp
from modules.ai_video_studio.ai_voice_clone.voice_analyzer import analyze_audio

_FEATURE_KEYS = [
    "f0_mean", "f0_std", "centroid_hz", "rolloff_hz", "brightness_hz",
    "rms", "vibrato_hz", "band_bass", "band_low_mid", "band_mid",
    "band_high_mid", "band_presence", "band_air",
]

# Typical ranges used to normalize features into [0, 1].
_RANGES = {
    "f0_mean": (60.0, 350.0), "f0_std": (0.0, 80.0),
    "centroid_hz": (200.0, 4000.0), "rolloff_hz": (1000.0, 9000.0),
    "brightness_hz": (500.0, 5000.0), "rms": (0.0, 0.5), "vibrato_hz": (0.0, 8.0),
    "band_bass": (0.0, 1.0), "band_low_mid": (0.0, 1.0), "band_mid": (0.0, 1.0),
    "band_high_mid": (0.0, 1.0), "band_presence": (0.0, 1.0), "band_air": (0.0, 1.0),
}


def encode_audio(audio: np.ndarray, *, sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    """Return a normalized embedding vector (float32, length 13)."""
    analysis = analyze_audio(audio, sample_rate=sample_rate)
    return encode_analysis(analysis)


def encode_analysis(analysis: dict[str, Any]) -> np.ndarray:
    vector = np.zeros(len(_FEATURE_KEYS), dtype=np.float32)
    for i, key in enumerate(_FEATURE_KEYS):
        value = float(analysis.get(key, 0.0))
        lo, hi = _RANGES[key]
        vector[i] = (value - lo) / (hi - lo)
    return np.clip(vector, 0.0, 1.0).astype(np.float32)


def encode_file(path: str, *, sample_rate: int = dsp.SAMPLE_RATE) -> np.ndarray:
    audio, sr = dsp.read_audio(path, target_sr=sample_rate)
    return encode_audio(audio, sample_rate=sr)


def feature_names() -> list[str]:
    return list(_FEATURE_KEYS)
