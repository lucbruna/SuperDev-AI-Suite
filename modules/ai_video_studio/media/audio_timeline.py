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
    downloads = get_downloads_dir().resolve()
    raw_path = Path(value).expanduser()
    candidate = (downloads / raw_path if not raw_path.is_absolute() else raw_path).resolve()
    roots = [get_subsystem_dir(name).resolve() for name in _AUDIO_DIRS]
    # Resolve symlinks before containment checks; reject arbitrary local files.
    if not any(candidate == root or root in candidate.parents for root in roots):
        raise ValueError("audio asset must be inside an approved generated-audio folder")
    if downloads not in candidate.parents:
        raise ValueError("audio asset is outside the downloads directory")
    if not candidate.is_file():
        raise ValueError(f"audio asset does not exist: {candidate.name}")
    return candidate


def list_audio_assets() -> list[dict[str, Any]]:
    """List generated audio assets using download-root-relative identifiers."""
    downloads = get_downloads_dir().resolve()
    allowed_extensions = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aiff", ".aif"}
    assets: list[dict[str, Any]] = []
    for folder in _AUDIO_DIRS:
        root = get_subsystem_dir(folder).resolve()
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in allowed_extensions:
                continue
            resolved = path.resolve()
            if root not in resolved.parents or downloads not in resolved.parents:
                continue
            assets.append({
                "asset": resolved.relative_to(downloads).as_posix(),
                "name": resolved.name,
                "folder": folder,
                "size_bytes": resolved.stat().st_size,
            })
    return assets


def _narration_activity_envelope(clips, *, total_samples, sample_rate, threshold_db, attack_seconds, release_seconds):
    """Return a smoothed speech-activity envelope for side-chain ducking."""
    block = max(1, int(round(sample_rate * 0.01)))
    activity = np.zeros(total_samples, dtype=np.float32)
    for clip in clips:
        if not isinstance(clip, dict) or clip.get("kind") != "narration":
            continue
        samples = clip.get("samples")
        if samples is None:
            continue
        audio = np.asarray(samples, dtype=np.float32).reshape(-1)
        start = max(0, int(round(float(clip.get("offset", clip.get("start", 0))) * sample_rate)))
        end = min(total_samples, start + len(audio))
        if end <= start: continue
        source = audio[:end - start]
        padded = np.pad(source, (0, (-len(source)) % block))
        if len(padded) == 0: continue
        rms = np.sqrt(np.mean(padded.reshape(-1, block) ** 2, axis=1))
        db = 20.0 * np.log10(np.maximum(rms, 1e-8))
        active = np.repeat((db >= threshold_db).astype(np.float32), block)[:len(source)]
        activity[start:end] = np.maximum(activity[start:end], active)
    if not np.any(activity): return activity
    attack = max(1, int(round(attack_seconds * sample_rate)))
    release = max(1, int(round(release_seconds * sample_rate)))
    envelope = np.zeros(total_samples, dtype=np.float32)
    current = 0.0
    for index, target in enumerate(activity):
        coefficient = 1.0 / (attack if target > current else release)
        current += (float(target) - current) * coefficient
        envelope[index] = current
    return envelope

def mix_audio_timeline(
    clips: list[dict[str, Any]],
    output_path: str | Path,
    *,
    total_duration: float,
    sample_rate: int = dsp.SAMPLE_RATE,
    ducking_enabled: bool = True,
    ducking_db: float = 9.0,
    ducking_threshold_db: float = -36.0,
    ducking_attack: float = 0.08,
    ducking_release: float = 0.35,
) -> dict[str, Any]:
    """Mix music/SFX/narration clips into one mono WAV with bounded envelopes.

    Each clip supports asset, start, end, trim_start, volume (0..2),
    fade_in, fade_out and explicit loop. Looping is opt-in and intended for
    background music; source audio is otherwise never repeated implicitly.
    """
    if not np.isfinite(total_duration) or total_duration <= 0:
        raise ValueError("total_duration must be a positive finite number")
    if not isinstance(sample_rate, int) or sample_rate < 8000:
        raise ValueError("sample_rate must be an integer >= 8000")
    ducking_values = (ducking_db, ducking_threshold_db, ducking_attack, ducking_release)
    if not all(np.isfinite(value) for value in ducking_values): raise ValueError("ducking controls must be finite")
    if not 0 <= ducking_db <= 24 or ducking_attack <= 0 or ducking_release <= 0:
        raise ValueError("ducking reduction must be 0..24 dB and attack/release must be positive")
    total_samples = int(round(total_duration * sample_rate))
    mix = np.zeros(total_samples, dtype=np.float64)
    reports: list[dict[str, Any]] = []
    speech_envelope = (_narration_activity_envelope(clips, total_samples=total_samples, sample_rate=sample_rate, threshold_db=ducking_threshold_db, attack_seconds=ducking_attack, release_seconds=ducking_release) if ducking_enabled and ducking_db > 0 else np.zeros(total_samples, dtype=np.float32))
    duck_floor = float(10 ** (-ducking_db / 20.0))

    for index, clip in enumerate(clips):
        if not isinstance(clip, dict):
            raise ValueError(f"audio clip {index} must be an object")
        raw_samples = clip.get("samples")
        asset = None if raw_samples is not None else validate_audio_asset(
            clip.get("asset") or clip.get("audio_path") or clip.get("path")
        )
        start = float(clip.get("start", clip.get("offset", 0)))
        default_end = start + len(raw_samples) / sample_rate if raw_samples is not None else total_duration
        end = float(clip.get("end", default_end))
        trim_start = float(clip.get("trim_start", 0))
        volume = float(clip.get("volume", clip.get("gain", 1)))
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

        if raw_samples is not None:
            samples = np.asarray(raw_samples, dtype=np.float32).reshape(-1)
            source_rate = sample_rate
        else:
            samples, source_rate = dsp.read_audio(asset, target_sr=sample_rate)
            if source_rate != sample_rate:
                samples = dsp.resample(samples, int(round(len(samples) * sample_rate / source_rate)))
        source_start = int(round(trim_start * sample_rate))
        count = int(round(duration * sample_rate))
        segment = np.asarray(samples[source_start:], dtype=np.float32)
        if len(segment) == 0:
            raise ValueError(f"audio clip {index} trim starts beyond the source asset")
        if bool(clip.get("loop", False)) and len(segment) < count:
            segment = np.tile(segment, int(np.ceil(count / len(segment))))
        placed = np.zeros(count, dtype=np.float32)
        placed[:min(count, len(segment))] = segment[:count]
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
            visible = placed[:destination_end - destination_start]
            if clip.get("kind") == "music" and ducking_enabled and ducking_db > 0:
                speech = speech_envelope[destination_start:destination_end]
                visible = visible * (1.0 - speech * (1.0 - duck_floor))
            mix[destination_start:destination_end] += visible
        reports.append({
            "index": index,
            "status": "mixed",
            "asset": asset.name if asset is not None else "narration",
            "start": round(start, 3),
            "duration": round(duration, 3),
            "volume": volume,
            "loop": bool(clip.get("loop", False)),
            "kind": str(clip.get("kind", "unspecified")),
            "ducking_applied": bool(clip.get("kind") == "music" and ducking_enabled and ducking_db > 0 and np.any(speech_envelope)),
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
        "ducking": {"enabled": bool(ducking_enabled and ducking_db > 0), "reduction_db": float(ducking_db), "threshold_db": float(ducking_threshold_db), "attack_seconds": float(ducking_attack), "release_seconds": float(ducking_release), "speech_detected": bool(np.any(speech_envelope))},
    }
