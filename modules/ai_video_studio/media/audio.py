"""Audio helpers — generate real audio files and mux into videos.

Produces WAV files with numpy (tone, noise) and can attach audio to a video
with FFmpeg. Used by the asset library (sound/music) and video finishing.
"""
from __future__ import annotations

import logging
import math
import subprocess
import wave
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

SAMPLE_RATE = 44100


def write_wav(path: str | Path, samples: np.ndarray, *, sample_rate: int = SAMPLE_RATE) -> Path:
    """Write a float numpy array ([-1, 1]) to a real WAV file."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    pcm = np.clip(samples, -1.0, 1.0)
    pcm16 = (pcm * 32767).astype(np.int16)
    with wave.open(str(out), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(pcm16.tobytes())
    return out


def tone(frequency: float = 440.0, duration: float = 2.0, *, amplitude: float = 0.5, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Generate a sine wave."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return (amplitude * np.sin(2 * math.pi * frequency * t)).astype(np.float32)


def chord(frequencies: list[float], duration: float = 2.0, *, amplitude: float = 0.4, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Generate a chord from multiple sine frequencies."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    samples = np.zeros_like(t, dtype=np.float32)
    for freq in frequencies:
        samples += amplitude * np.sin(2 * math.pi * freq * t)
    return (samples / max(1, len(frequencies))).astype(np.float32)


def white_noise(duration: float = 2.0, *, amplitude: float = 0.3, sample_rate: int = SAMPLE_RATE, seed: int = 0) -> np.ndarray:
    """Generate deterministic white noise."""
    rng = np.random.default_rng(seed)
    return (rng.uniform(-1, 1, int(sample_rate * duration)) * amplitude).astype(np.float32)


def silence(duration: float = 2.0, *, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    return np.zeros(int(sample_rate * duration), dtype=np.float32)


def mux_audio_into_video(video_path: str | Path, audio_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    """Attach audio while preserving the full video duration.

The audio is padded with silence when narration ends early, then ``-shortest``
uses the video stream as the limiting stream. This prevents a short TTS clip
from truncating the final frames of the rendered video.
"""
    import shutil

    video = Path(video_path)
    audio = Path(audio_path)
    if not video.is_file() or video.stat().st_size <= 0:
        return {"output_path": str(video), "muxed": False, "reason": "video input missing or empty"}
    if not audio.is_file() or audio.stat().st_size <= 0:
        return {"output_path": str(video), "muxed": False, "reason": "audio input missing or empty"}
    if shutil.which("ffmpeg") is None:
        return {"output_path": str(video), "muxed": False, "reason": "ffmpeg unavailable"}
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-af", "apad",
        "-shortest",
        str(out),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        logger.warning("Audio muxing timed out after 300 seconds")
        return {"output_path": str(video), "muxed": False, "reason": "audio muxing timed out"}
    except OSError as exc:
        logger.warning("Audio muxing could not start: %s", exc)
        return {"output_path": str(video), "muxed": False, "reason": "audio mux process could not start"}
    if result.returncode != 0:
        logger.warning("Audio muxing failed: %s", result.stderr[-300:])
        return {"output_path": str(video_path), "muxed": False, "reason": result.stderr[-200:]}
    if not out.is_file() or out.stat().st_size <= 0:
        logger.warning("Audio mux command succeeded without producing a non-empty output file")
        return {"output_path": str(video), "muxed": False, "reason": "mux output missing or empty"}
    return {"output_path": str(out), "muxed": True, "bytes": out.stat().st_size}
