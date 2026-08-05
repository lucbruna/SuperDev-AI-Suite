"""Speech Alignment — places synthesized clips on the dub timeline.

Each synthesized line is time-stretched (phase vocoder, pitch preserved) to
its allocated slot so the final dub fits the video exactly.
"""
from __future__ import annotations

from typing import Any


from modules.ai_video_studio.media import dsp

MAX_STRETCH = 1.6
MIN_STRETCH = 0.5


def place_clips(lines: list[dict[str, Any]], *, sample_rate: int = dsp.SAMPLE_RATE) -> list[dict[str, Any]]:
    """``lines`` entries: ``{text, start, end, audio_path}``.

    Returns track entries ``{samples, offset, gain}`` ready for mixing.
    """
    tracks: list[dict[str, Any]] = []
    for line in lines:
        audio, sr = dsp.read_audio(line["audio_path"], target_sr=sample_rate)
        slot = max(0.4, line["end"] - line["start"])
        current = len(audio) / sample_rate
        if current > 0:
            rate = current / slot
            rate = max(MIN_STRETCH, min(MAX_STRETCH, rate))
            audio = dsp.time_stretch(audio, rate)
        audio = dsp.normalize_peak(audio, 0.9)
        tracks.append({
            "samples": audio,
            "offset": line["start"],
            "gain": line.get("gain", 1.0),
            "line": line.get("text", ""),
        })
    return tracks
