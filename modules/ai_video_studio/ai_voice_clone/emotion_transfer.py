"""Emotion Transfer — derives prosody (rate/pitch/energy) from a reference.

The source sample's measured f0 spread, vibrato and dynamics are mapped to
synthesis prosody so cloned speech carries the same emotional texture.
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_voice_clone.voice_analyzer import analyze_file


def transfer_emotion(reference_path: str, *, emotion: str | None = None) -> dict[str, float]:
    """Return ``{rate, pitch, energy, vibrato}`` prosody for a reference sample."""
    analysis = analyze_file(reference_path)

    # Faster speech when dynamic range is compressed (excited feel).
    dynamics = analysis["snr_db"]
    rate = 1.0 + max(-0.1, min(0.15, (60.0 - dynamics) / 200.0))
    # Relative pitch: compare to a neutral male f0 baseline (~120 Hz).
    f0 = analysis["f0_mean"] or 120.0
    pitch = max(0.7, min(1.4, f0 / 120.0))
    # Energy from RMS, normalized against a comfortable narration level.
    energy = max(0.2, min(1.0, analysis["rms"] / 0.1))
    vibrato = min(0.08, analysis["vibrato_hz"] / 100.0)

    if emotion:
        from modules.ai_video_studio.ai_voice_studio.synthesis.emotion_controller import emotion_prosody

        p = emotion_prosody(emotion)
        rate *= p["rate"]
        pitch *= p["pitch"]
        energy = max(energy, p["energy"])
        vibrato = max(vibrato, p["vibrato"])

    return {
        "rate": round(rate, 3),
        "pitch": round(pitch, 3),
        "energy": round(energy, 3),
        "vibrato": round(vibrato, 3),
        "_analysis": {k: analysis[k] for k in ("f0_mean", "f0_std", "rms", "snr_db")},
    }


def prosody_from_analysis(analysis: dict[str, Any]) -> dict[str, float]:
    """Same mapping but from an already-computed analysis dict."""
    f0 = analysis.get("f0_mean") or 120.0
    dynamics = analysis.get("snr_db", 40.0)
    rate = 1.0 + max(-0.1, min(0.15, (60.0 - dynamics) / 200.0))
    return {
        "rate": round(rate, 3),
        "pitch": round(max(0.7, min(1.4, f0 / 120.0)), 3),
        "energy": round(max(0.2, min(1.0, (analysis.get("rms") or 0.05) / 0.1)), 3),
        "vibrato": round(min(0.08, (analysis.get("vibrato_hz") or 0.0) / 100.0), 3),
    }
