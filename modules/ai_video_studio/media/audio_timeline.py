"""Frame-independent audio timeline mixer for edited DARKSTUDIO renders.

Only generated audio assets inside approved download folders may be referenced.
Clip times are seconds at the API boundary; the final mix is fixed to the video
duration and uses per-clip trim, gain and fade envelopes.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from modules.ai_video_studio.media import dsp
from modules.ai_video_studio.media.output_paths import get_downloads_dir, get_subsystem_dir


_AUDIO_DIRS = ("voice", "music", "effects", "dubbing", "mix")


def validate_audio_asset(value: Any) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("audio clip asset must be a non-empty path")
    candidate = Path(value).expanduser().resolve()
    roots = [get_subsystem_dir(name).resolve() for name in _AUDIO_DIRS]
    downloads = get_downloads_dir().resolve()
    # Resolve symlinks before containment checks; reject arbitrary local files.
    if not any(candidate == root or root in candidate.parents for root in roots):
        raise ValueError("audio asset must be inside an approved generated-audio folder")
    if downloads not in candidate.parents:
        raise ValueError("audio asset is outside the downloads directory")
    if not candidate.is_file():
        raise ValueError(f"audio asset does not exist: {candidate.name}")
    return candidate


def mix_audio_timeline(
    clips: list[dict[str, Any]],
    output_path: str | Path,
    *,
    total_duration: float,
    sample_rate: int = dsp.SAMPLE_RATE,
) -> dict[str, Any]:
    """Mix music/SFX/narration clips into one mono WAV with bounded envelopes.

    Each clip supports asset, start, end, trim_start, volume (0..2),
    fade_in and fade_out. The clip's selected source segment is fitted to its
    timeline interval without time-stretching. The mix never exceeds the
    requested video duration.
    """
    if not np.isfinite(total_duration) or total_duration <= 0:
        raise ValueError("total_duration must be a positive finite number")
    if not isinstance(sample_rate, int) or sample_rate < 8000:
        raise ValueError("sample_rate must be an integer >= 8000")
    total_samples = int(round(total_duration * sample_rate))
    mix = np.zeros(total_samples, dtype=np.float64)
    reports: list[dict[str, Any]] = []

    for index, clip in enumerate(clips):
        if not isinstance(clip, dict):
            raise ValueError(f"audio clip {index} must be an object")
        asset = validate_audio_asset(clip.get("asset") or clip.get("audio_path") or clip.get("path"))
        start = float(clip.get("start", 0))
        end = float(clip.get("end", total_duration))
        trim_start = float(clip.get("trim_start", 0))
        volume = float(clip.get("volume", 1))
        fade_in = float(clip.get("fade_in", 0))
        fade_out = float(clip.get("fade_out", 0))
        values = (start, end, trim_start, volume, fade_in, fade_out)
        if not all(np.isfinite(v) for v in values):
            raise ValueError(f"audio clip {index} values must be finite")
        if start < 0 or end <= start or trim_start < 0:
            raise ValueError(f"audio clip {index} has invalid timing or trim")
        if not 0 <= volume <= 2:
            raise ValueError(f"audio clip {index} volume must be between 0 and 2")
        duration = min(end, total_duration) - start
        if duration <= 0:
            reports.append({"index": index, "status": "outside_video"})
            continue
        if fade_in < 0 or fade_out < 0 or fade_in > duration or fade_out > duration:
            raise ValueError(f"audio clip {index} fade exceeds its timeline duration")

        samples, source_rate = dsp.read_audio(asset, target_sr=sample_rate)
        if source_rate != sample_rate:
            samples = dsp.resample(samples, int(round(len(samples) * sample_rate / source_rate)))
        source_start = int(round(trim_start * sample_rate))
        count = int(round(duration * sample_rate))
        segment = np.asarray(samples[source_start:source_start + count], dtype=np.float32)
        if len(segment) == 0:
            raise ValueError(f"audio clip {index} trim starts beyond the source asset")
        # A clip is never looped implicitly. Short sources end in silence.
        placed = np.zeros(count, dtype=np.float32)
        placed[:len(segment)] = segment
        envelope = np.ones(count, dtype=np.float32)
        fade_in_samples = min(count, int(round(fade_in * sample_rate)))
        fade_out_samples = min(count, int(round(fade_out * sample_rate)))
        if fade_in_samples:
            envelope[:fade_in_samples] *= np.linspace(0, 1, fade_in_samples, endpoint=True)
        if fade_out_samples:
            envelope[-fade_out_samples:] *= np.linspace(1, 0, fade_out_samples, endpoint=True)
        placed *= envelope * volume

        destination_start = int(round(start * sample_rate))
        destination_end = min(total_samples, destination_start + count)
        if destination_end > destination_start:
            mix[destination_start:destination_end] += placed[:destination_end - destination_start]
        reports.append({
            "index": index,
            "status": "mixed",
            "asset": asset.name,
            "start": round(start, 3),
            "duration": round(duration, 3),
            "volume": volume,
        })

    limited = dsp.limiter(mix.astype(np.float32), threshold=0.97, sample_rate=sample_rate)
    out = dsp.write_audio(output_path, limited, sample_rate=sample_rate)
    return {
        "output_path": str(out),
        "duration": round(len(limited) / sample_rate, 3),
        "sample_rate": sample_rate,
        "clip_count": len(reports),
        "clips": reports,
        "peak": round(dsp.peak(limited), 4),
    }
