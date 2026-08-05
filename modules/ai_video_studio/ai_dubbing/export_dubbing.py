"""Export Dubbing — renders the final dubbed audio and muxes it into the video."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from modules.ai_video_studio.media import dsp
from modules.ai_video_studio.media.audio import mux_audio_into_video


def export_audio_track(tracks: list[dict[str, Any]], output_path: str | Path, *,
                       total_duration: float | None = None) -> dict[str, Any]:
    """Mix the placed clips into one WAV file."""
    mixed = dsp.mix_tracks(tracks, total_duration=total_duration)
    mixed = dsp.limiter(mixed, 0.97)
    mixed = dsp.normalize_peak(mixed, 0.95)
    out = Path(output_path)
    dsp.write_audio(out, mixed)
    return {"output_path": str(out), "bytes": out.stat().st_size,
            "duration": round(len(mixed) / dsp.SAMPLE_RATE, 3)}


def mux_dubbed_video(video_path: str, audio_track: str, output_path: str | Path) -> dict[str, Any]:
    """Attach the dubbed track to the original video."""
    return mux_audio_into_video(video_path, audio_track, output_path)


def probe_duration(media_path: str) -> float:
    """Return media duration via ffprobe (0.0 on failure)."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", media_path],
            capture_output=True, text=True, timeout=60,
        )
        return float(result.stdout.strip())
    except (subprocess.SubprocessError, ValueError):
        return 0.0
