"""Offline TTS — voices that never need a network.

Primary: ``pyttsx3`` (OS speech). Last resort: a deterministic formant
synthesizer written in numpy that maps characters to vowel/consonant sound
units, producing real (robotic) speech audio with zero dependencies.
"""
from __future__ import annotations

import logging
import math
import os
from pathlib import Path

import numpy as np

from modules.ai_video_studio.media import dsp

logger = logging.getLogger(__name__)

# Vowel → three formant frequencies (F1, F2, F3) for a male-ish neutral timbre.
_FORMANTS = {
    "a": (730.0, 1090.0, 2440.0),
    "e": (530.0, 1840.0, 2480.0),
    "i": (270.0, 2290.0, 3010.0),
    "o": (570.0, 840.0, 2410.0),
    "u": (300.0, 870.0, 2240.0),
}

_CHAR_DURATION = 0.055   # seconds per voiced character at rate 1.0
_SILENCE_BETWEEN = 0.006


class OfflineTTS:
    """Produces a real WAV file with no network access."""

    def synthesize(
        self,
        text: str,
        *,
        output_path: str | None = None,
        rate: float = 1.0,
        pitch: float = 1.0,
        sample_rate: int = dsp.SAMPLE_RATE,
    ) -> dict:
        """Return ``{output_path, duration, engine}``, never raising."""
        if output_path is None:
            output_path = str(Path(__file__).resolve().parent.parent.parent.parent
                              / "downloads" / "voice" / "offline_voice.wav")
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        # 1) Try the OS speech engine (pyttsx3).
        try:
            import pyttsx3

            wav_path = str(out.with_suffix(".wav"))
            engine = pyttsx3.init()
            try:
                engine.setProperty("rate", int(180 * max(0.5, rate)))
                engine.save_to_file(text, wav_path)
                engine.runAndWait()
            finally:
                engine.stop()
            if os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
                return self._finish(wav_path, "pyttsx3")
        except Exception as e:  # noqa: BLE001
            logger.warning("pyttsx3 unavailable (%s), using formant synthesizer", e)

        # 2) Pure numpy formant synthesizer.
        samples = formant_synth(text, rate=rate, pitch=pitch, sample_rate=sample_rate)
        dsp.write_audio(out, samples, sample_rate=sample_rate)
        duration = len(samples) / sample_rate
        return {"output_path": str(out), "duration": round(duration, 3), "engine": "formant"}

    @staticmethod
    def _finish(path: str, engine: str) -> dict:
        import wave

        with wave.open(path, "rb") as w:
            frames = w.getnframes()
            sr = w.getframerate()
        return {"output_path": path, "duration": round(frames / sr, 3), "engine": engine}


def formant_synth(
    text: str,
    *,
    rate: float = 1.0,
    pitch: float = 1.0,
    f0: float = 120.0,
    sample_rate: int = dsp.SAMPLE_RATE,
) -> np.ndarray:
    """Synthesize speech-like audio from text using formant resonators."""
    chunks: list[np.ndarray] = []
    prev_word = False
    for ch in text.lower():
        if ch.isalpha():
            dur = _CHAR_DURATION / max(0.25, rate)
            if ch in _FORMANTS:
                chunks.append(_vowel(ch, f0 * pitch, dur, sample_rate))
            else:
                chunks.append(_consonant(dur, sample_rate))
            prev_word = False
        elif ch in " \t\n":
            if not prev_word:
                chunks.append(np.zeros(int(_SILENCE_BETWEEN * sample_rate), dtype=np.float32))
                prev_word = True
        elif ch in ".!?…":
            chunks.append(np.zeros(int(0.32 * sample_rate / max(0.25, rate)), dtype=np.float32))
        elif ch in ",;:—-":
            chunks.append(np.zeros(int(0.16 * sample_rate / max(0.25, rate)), dtype=np.float32))

    if not chunks:
        chunks = [np.zeros(int(0.5 * sample_rate), dtype=np.float32)]
    speech = np.concatenate(chunks)
    speech = dsp.fade_io(speech, fade_in=0.01, fade_out=0.05, sample_rate=sample_rate)
    return dsp.normalize_peak(speech, 0.9)


def _vowel(vowel: str, f0: float, duration: float, sample_rate: int) -> np.ndarray:
    n = int(duration * sample_rate)
    t = np.arange(n) / sample_rate
    # Pulse train of the fundamental plus 10 harmonics (glottal source).
    sig = np.zeros(n, dtype=np.float32)
    for k in range(1, 11):
        sig += (1.0 / k) * np.sin(2 * math.pi * f0 * k * t)
    sig /= 10.0
    # Resonate through the vowel's three formants.
    f1, f2, f3 = _FORMANTS[vowel]
    sig = dsp.biquad_peak(sig, f1, 4.0, 14.0, sample_rate=sample_rate)
    sig = dsp.biquad_peak(sig, f2, 4.0, 12.0, sample_rate=sample_rate)
    sig = dsp.biquad_peak(sig, f3, 4.0, 8.0, sample_rate=sample_rate)
    # Attack/release so consonants don't click.
    env = np.ones(n, dtype=np.float32)
    a = max(1, int(0.008 * sample_rate))
    r = max(1, int(0.02 * sample_rate))
    env[:a] = np.linspace(0, 1, a, dtype=np.float32)
    env[-r:] *= np.linspace(1, 0, r, dtype=np.float32)
    return (sig * env).astype(np.float32)


def _consonant(duration: float, sample_rate: int) -> np.ndarray:
    n = int(duration * sample_rate)
    noise = dsp.noise_white(duration, sample_rate=sample_rate)
    noise = dsp.one_pole_hp(noise, 1800.0, sample_rate=sample_rate)
    noise = dsp.biquad_peak(noise, 4200.0, 1.5, 10.0, sample_rate=sample_rate)
    # noise_white uses round() while n truncates — align exact lengths.
    noise = noise[:n]
    env = dsp.exp_decay(n, tau=0.02, sample_rate=sample_rate)
    return (noise * env * 0.6).astype(np.float32)
