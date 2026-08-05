"""Speech Recognition — transcribes audio to timed segments.

1. ``faster-whisper`` / ``whisper`` when installed (real ASR).
2. Energy-based VAD segmentation when no model is available (real timing,
   text supplied by the caller or empty).

Never raises: always returns segments + engine used.
"""
from __future__ import annotations

import logging
from typing import Any

from modules.ai_video_studio.media import dsp

logger = logging.getLogger(__name__)


def transcribe(audio_path: str, *, language: str | None = None) -> dict[str, Any]:
    """Return ``{segments: [{start, end, text}], engine}``."""
    try:
        return _transcribe_faster_whisper(audio_path, language=language)
    except Exception as e:  # noqa: BLE001
        logger.info("faster-whisper unavailable (%s), using VAD segmentation", e)
    return _vad_segments(audio_path)


def _transcribe_faster_whisper(audio_path: str, *, language: str | None) -> dict[str, Any]:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise RuntimeError("faster-whisper not installed") from None

    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments_iter, _info = model.transcribe(audio_path, language=language, beam_size=1)
    segments = [
        {"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip()}
        for s in segments_iter
        if s.text and s.text.strip()
    ]
    return {"segments": segments, "engine": "faster-whisper"}


def _vad_segments(audio_path: str, *, frame: int = 1024, hop: int = 512,
                  threshold: float = 0.008, min_span: float = 0.6) -> dict[str, Any]:
    """Energy-based voice activity detection producing speech spans."""
    audio, sr = dsp.read_audio(audio_path)
    n = len(audio)
    energies: list[float] = []
    times: list[float] = []
    for start in range(0, n - frame, hop):
        block = audio[start:start + frame]
        energies.append(float(dsp.rms(block)))
        times.append(start / sr)

    active = [e > threshold for e in energies]
    segments: list[dict[str, Any]] = []
    in_speech = False
    span_start = 0.0
    for i, is_active in enumerate(active):
        if is_active and not in_speech:
            in_speech = True
            span_start = times[i]
        elif not is_active and in_speech:
            in_speech = False
            duration = times[i] - span_start
            if duration >= min_span:
                segments.append({"start": round(span_start, 3), "end": round(times[i], 3), "text": ""})
    if in_speech:
        end = times[-1] if times else n / sr
        if end - span_start >= min_span:
            segments.append({"start": round(span_start, 3), "end": round(end, 3), "text": ""})
    return {"segments": segments, "engine": "vad"}
