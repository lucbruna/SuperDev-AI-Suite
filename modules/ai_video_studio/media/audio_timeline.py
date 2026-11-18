"""Frame-independent audio timeline mixer for edited DARKSTUDIO renders.

Only generated audio assets inside approved download folders may be referenced.
Clip times are seconds at the API boundary; the final mix is fixed to the video
duration and uses per-clip trim, gain and fade envelopes.
"""
from __future__ import annotations

from pathlib import Path
import json
import subprocess
import tempfile
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
        audio = np.asarray(samples, dtype=np.float32)
        if audio.ndim == 1:
            audio = audio[:, None]
        if audio.ndim != 2:
            continue
        mono = np.mean(audio, axis=1, dtype=np.float32)
        start = max(0, int(round(float(clip.get("offset", clip.get("start", 0))) * sample_rate)))
        end = min(total_samples, start + len(mono))
        if end <= start: continue
        source = mono[:end - start]
        padded = np.pad(source, (0, (-len(source)) % block))
        if len(padded) == 0: continue
        rms = np.sqrt(np.mean(padded.reshape(-1, block) ** 2, axis=1))
        db = 20.0 * np.log10(np.maximum(rms, 1e-8))
        active = np.repeat((db >= threshold_db).astype(np.float32), block)[:len(source)]
        activity[start:end] = np.maximum(activity[start:end], active)
    if not np.any(activity): return activity
    padded_activity = np.pad(activity, (0, (-total_samples) % block))
    block_activity = padded_activity.reshape(-1, block).max(axis=1)
    attack_blocks = max(1, int(round(attack_seconds * sample_rate / block)))
    release_blocks = max(1, int(round(release_seconds * sample_rate / block)))
    block_envelope = np.zeros(len(block_activity), dtype=np.float32)
    current = 0.0
    for index, target in enumerate(block_activity):
        coefficient = 1.0 / (attack_blocks if target > current else release_blocks)
        current += (float(target) - current) * coefficient
        block_envelope[index] = current
    return np.repeat(block_envelope, block)[:total_samples]


def _ffmpeg_loudnorm_pass(input_path: Path, output_path: Path | None, *, target_lufs: float, true_peak_db: float, lra: float, measured: dict[str, float] | None = None) -> dict[str, float]:
    """Run FFmpeg loudnorm once and return its measured loudness JSON."""
    if measured is None:
        filt = f"loudnorm=I={target_lufs}:TP={true_peak_db}:LRA={lra}:print_format=json"
    else:
        filt = (
            f"loudnorm=I={target_lufs}:TP={true_peak_db}:LRA={lra}:"
            f"measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:"
            f"measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:"
            f"offset={measured['target_offset']}:linear=true:print_format=json"
        )
    command = ["ffmpeg", "-hide_banner", "-nostats", "-i", str(input_path), "-af", filt]
    if output_path is None:
        command += ["-f", "null", "-"]
    else:
        command += ["-ar", "44100", "-c:a", "pcm_s24le", "-y", str(output_path)]
    result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg loudnorm failed: {(result.stderr or result.stdout)[-1200:]}")
    stderr = result.stderr or ""
    end = stderr.rfind("}")
    start = stderr.rfind("{", 0, end)
    if start < 0 or end < 0:
        raise RuntimeError("FFmpeg loudnorm did not return its measurement report")
    try:
        report = json.loads(stderr[start:end + 1])
        keys = ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset")
        values = {key: float(report[key]) for key in keys}
        if not all(np.isfinite(value) for value in values.values()):
            raise ValueError("loudnorm measurement is not finite (the source may be silent)")
        return values
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError("FFmpeg loudnorm returned an invalid measurement report") from exc


def normalize_loudness_file(path: str | Path, *, target_lufs: float = -14.0, true_peak_db: float = -1.0, lra: float = 11.0) -> dict[str, float | bool]:
    """Apply FFmpeg two-pass EBU R128 loudness normalization in-place."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(source)
    if not all(np.isfinite(value) for value in (target_lufs, true_peak_db, lra)):
        raise ValueError("LUFS normalization values must be finite")
    if not -36 <= target_lufs <= -5 or not -9 <= true_peak_db <= 0 or not 1 <= lra <= 20:
        raise ValueError("LUFS target must be -36..-5, true peak -9..0 dBTP, and LRA 1..20")
    measured = _ffmpeg_loudnorm_pass(source, None, target_lufs=target_lufs, true_peak_db=true_peak_db, lra=lra)
    with tempfile.NamedTemporaryFile(suffix=".wav", dir=str(source.parent), delete=False) as tmp:
        temporary = Path(tmp.name)
    try:
        output_report = _ffmpeg_loudnorm_pass(source, temporary, target_lufs=target_lufs, true_peak_db=true_peak_db, lra=lra, measured=measured)
        normalized, rate = dsp.read_audio(temporary, target_sr=44100, preserve_channels=True)
        safe = dsp.limiter(normalized, threshold=float(10 ** (true_peak_db / 20.0)), sample_rate=rate)
        dsp.write_audio(source, safe, sample_rate=rate)
        verified = _ffmpeg_loudnorm_pass(source, None, target_lufs=target_lufs, true_peak_db=true_peak_db, lra=lra)
        return {"target_lufs": target_lufs, "true_peak_db": true_peak_db, "input_i": measured["input_i"], "input_tp": measured["input_tp"], "input_lra": measured["input_lra"], "output_i": verified["input_i"], "output_tp": verified["input_tp"], "output_lra": verified["input_lra"], "normalization_pass_i": output_report["input_i"], "passes": 2.0, "verified": True}
    finally:
        temporary.unlink(missing_ok=True)

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
    normalization_enabled: bool = True,
    normalization_target_dbfs: float = -18.0,
    normalization_max_gain_db: float = 6.0,
    loudness_normalization_enabled: bool = False,
    target_lufs: float = -14.0,
    true_peak_db: float = -1.0,
    loudness_range: float = 11.0,
) -> dict[str, Any]:
    """Mix music/SFX/narration clips into a stereo WAV with bounded envelopes.

    Each clip supports asset, start, end, trim_start, volume (0..2),
    fade_in, fade_out and explicit loop. Looping is opt-in and intended for
    background music; source audio is otherwise never repeated implicitly.
    """
    if not np.isfinite(total_duration) or total_duration <= 0:
        raise ValueError("total_duration must be a positive finite number")
    if not isinstance(sample_rate, int) or sample_rate < 8000:
        raise ValueError("sample_rate must be an integer >= 8000")
    ducking_values = (ducking_db, ducking_threshold_db, ducking_attack, ducking_release, normalization_target_dbfs, normalization_max_gain_db)
    if not all(np.isfinite(value) for value in ducking_values): raise ValueError("ducking controls must be finite")
    if not 0 <= ducking_db <= 24 or ducking_attack <= 0 or ducking_release <= 0:
        raise ValueError("ducking reduction must be 0..24 dB and attack/release must be positive")
    if not -60 <= normalization_target_dbfs <= 0 or not 0 <= normalization_max_gain_db <= 24:
        raise ValueError("normalization target must be -60..0 dBFS and max gain 0..24 dB")
    if not all(np.isfinite(value) for value in (target_lufs, true_peak_db, loudness_range)) or not -36 <= target_lufs <= -5 or not -9 <= true_peak_db <= 0 or not 1 <= loudness_range <= 20:
        raise ValueError("LUFS target must be -36..-5, true peak -9..0 dBTP, and LRA 1..20")
    total_samples = int(round(total_duration * sample_rate))
    output_channels = 2
    mix = np.zeros((total_samples, output_channels), dtype=np.float64)
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
        pan = float(clip.get("pan", 0))
        values = (start, end, trim_start, volume, fade_in, fade_out, pan)
        if not all(np.isfinite(v) for v in values):
            raise ValueError(f"audio clip {index} values must be finite")
        if start < 0 or end <= start or trim_start < 0:
            raise ValueError(f"audio clip {index} has invalid timing or trim")
        if not 0 <= volume <= 2:
            raise ValueError(f"audio clip {index} volume must be between 0 and 2")
        if not -1 <= pan <= 1:
            raise ValueError(f"audio clip {index} pan must be between -1 and 1")
        duration = min(end, total_duration) - start
        if duration <= 0:
            reports.append({"index": index, "status": "outside_video"})
            continue
        if fade_in < 0 or fade_out < 0 or fade_in > duration or fade_out > duration:
            raise ValueError(f"audio clip {index} fade exceeds its timeline duration")

        if raw_samples is not None:
            samples = np.asarray(raw_samples, dtype=np.float32)
            source_rate = sample_rate
        else:
            samples, source_rate = dsp.read_audio(asset, target_sr=sample_rate, preserve_channels=True)
            if source_rate != sample_rate:
                samples = dsp.resample(samples, int(round(len(samples) * sample_rate / source_rate)))
        if samples.ndim == 1:
            samples = samples[:, None]
        if samples.ndim != 2 or samples.shape[1] not in (1, 2):
            raise ValueError(f"audio clip {index} must contain mono or stereo samples")
        if samples.shape[1] == 1:
            samples = np.repeat(samples, 2, axis=1)
        source_start = int(round(trim_start * sample_rate))
        count = int(round(duration * sample_rate))
        segment = np.asarray(samples[source_start:], dtype=np.float32)
        if len(segment) == 0:
            raise ValueError(f"audio clip {index} trim starts beyond the source asset")
        if bool(clip.get("loop", False)) and len(segment) < count:
            segment = np.tile(segment, int(np.ceil(count / len(segment))))
        placed = np.zeros((count, output_channels), dtype=np.float32)
        placed[:min(count, len(segment))] = segment[:count]
        envelope = np.ones(count, dtype=np.float32)
        fade_in_samples = min(count, int(round(fade_in * sample_rate)))
        fade_out_samples = min(count, int(round(fade_out * sample_rate)))
        if fade_in_samples:
            envelope[:fade_in_samples] *= np.linspace(0, 1, fade_in_samples, endpoint=True)
        if fade_out_samples:
            envelope[-fade_out_samples:] *= np.linspace(1, 0, fade_out_samples, endpoint=True)
        placed *= envelope[:, None] * volume
        # Balance controls move the signal left/right without changing stereo phase.
        if pan < 0:
            placed[:, 1] *= 1.0 + pan
        elif pan > 0:
            placed[:, 0] *= 1.0 - pan

        destination_start = int(round(start * sample_rate))
        destination_end = min(total_samples, destination_start + count)
        if destination_end > destination_start:
            visible = placed[:destination_end - destination_start]
            if clip.get("kind") == "music" and ducking_enabled and ducking_db > 0:
                speech = speech_envelope[destination_start:destination_end]
                visible = visible * (1.0 - speech[:, None] * (1.0 - duck_floor))
            mix[destination_start:destination_end] += visible
        reports.append({
            "index": index,
            "status": "mixed",
            "asset": asset.name if asset is not None else "narration",
            "start": round(start, 3),
            "duration": round(duration, 3),
            "volume": volume,
            "pan": pan,
            "loop": bool(clip.get("loop", False)),
            "kind": str(clip.get("kind", "unspecified")),
            "ducking_applied": bool(clip.get("kind") == "music" and ducking_enabled and ducking_db > 0 and np.any(speech_envelope)),
        })

    mixed = mix.astype(np.float32)
    pre_normalization_rms = dsp.rms(mixed)
    normalization_gain_db = 0.0
    if normalization_enabled and not loudness_normalization_enabled and pre_normalization_rms > 1e-9:
        target_rms = float(10 ** (normalization_target_dbfs / 20.0))
        requested_gain_db = 20.0 * np.log10(target_rms / pre_normalization_rms)
        normalization_gain_db = min(float(normalization_max_gain_db), float(requested_gain_db))
        mixed = (mixed * float(10 ** (normalization_gain_db / 20.0))).astype(np.float32)
    limited = mixed if loudness_normalization_enabled else dsp.limiter(mixed, threshold=0.97, sample_rate=sample_rate)
    out = dsp.write_audio(output_path, limited, sample_rate=sample_rate)
    loudness_report = None
    if loudness_normalization_enabled:
        loudness_report = normalize_loudness_file(out, target_lufs=target_lufs, true_peak_db=true_peak_db, lra=loudness_range)
        limited, _ = dsp.read_audio(out, target_sr=sample_rate, preserve_channels=True)
    return {
        "output_path": str(out),
        "duration": round(len(limited) / sample_rate, 3),
        "sample_rate": sample_rate,
        "channels": output_channels,
        "channel_layout": "stereo",
        "clip_count": len(reports),
        "clips": reports,
        "peak": round(dsp.peak(limited), 4),
        "normalization": {"enabled": bool(normalization_enabled and not loudness_normalization_enabled), "bypassed_for_loudness": bool(loudness_normalization_enabled), "target_dbfs": float(normalization_target_dbfs), "gain_db": round(normalization_gain_db, 3), "pre_rms": round(pre_normalization_rms, 6)},
        "loudness": {"enabled": bool(loudness_normalization_enabled), **(loudness_report or {})},
        "ducking": {"enabled": bool(ducking_enabled and ducking_db > 0), "reduction_db": float(ducking_db), "threshold_db": float(ducking_threshold_db), "attack_seconds": float(ducking_attack), "release_seconds": float(ducking_release), "speech_detected": bool(np.any(speech_envelope))},
    }
