"""Mixer Engine — mixes tracks with per-track EQ/pan/gain and a master bus.

Every track entry: ``{samples, gain=1.0, pan=0.0, eq=[(freq, db, q)...]}``.
The master chain runs EQ preset → compressor → limiter → loudness
normalization. Output is a real audio file plus the processed buffer.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np

from modules.ai_video_studio.media import dsp
from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
from modules.ai_video_studio.ai_audio_mixer.equalizer import eq, apply_preset
from modules.ai_video_studio.ai_audio_mixer.compressor import compress
from modules.ai_video_studio.ai_audio_mixer.limiter import limit
from modules.ai_video_studio.ai_audio_mixer.loudness_normalizer import normalize, estimate_loudness

logger = logging.getLogger(__name__)

_MIXER = None


def get_mixer_engine() -> MixerEngine:
    global _MIXER
    if _MIXER is None:
        _MIXER = MixerEngine()
    return _MIXER


class MixerEngine:
    """Mixes any number of tracks into one real audio file."""

    def mix(self, tracks: list[dict[str, Any]], *, master_preset: str = "flat",
            output_path: str | None = None, write_file: bool = True) -> dict[str, Any]:
        if not tracks:
            raise ValueError("No tracks to mix")
        # Per-track processing.
        processed: list[np.ndarray] = []
        length = 0
        for track in tracks:
            samples = np.asarray(track["samples"], dtype=np.float32).reshape(-1)
            if track.get("eq"):
                samples = eq(samples, track["eq"])
            gain = float(track.get("gain", 1.0))
            pan = float(track.get("pan", 0.0))
            stereo = dsp.to_stereo(samples, pan=pan) * gain
            processed.append(stereo)
            length = max(length, len(samples))

        # Sum stereo buses.
        mix = np.zeros((length, 2), dtype=np.float64)
        for stereo in processed:
            n = len(stereo)
            mix[:n] += stereo

        # Master chain.
        mono_mix = np.mean(mix, axis=-1)
        mono_mix = apply_preset(mono_mix, master_preset)
        mono_mix = compress(mono_mix, threshold_db=-18.0, ratio=2.5)
        mono_mix = limit(mono_mix, threshold=0.97)
        mono_mix = normalize(mono_mix, target_rms=0.24, target_peak=0.95)

        result: dict[str, Any] = {
            "samples": mono_mix,
            "duration": round(len(mono_mix) / dsp.SAMPLE_RATE, 3),
            "tracks": len(tracks),
            "loudness": estimate_loudness(mono_mix),
        }
        if write_file:
            out_dir = Path(output_path).parent if output_path else get_subsystem_dir("mix")
            out_path = output_path or str(unique_filename(out_dir, "mix", "wav"))
            dsp.write_audio(out_path, mono_mix)
            result["output_path"] = out_path
            result["bytes"] = int(Path(out_path).stat().st_size)
        return result
