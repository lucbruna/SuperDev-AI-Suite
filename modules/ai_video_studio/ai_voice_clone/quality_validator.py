"""Quality Validator — checks a sample is usable for cloning."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_voice_clone.voice_analyzer import analyze_file

MIN_DURATION = 2.0
MAX_DURATION = 600.0
MIN_SNR = 8.0
MAX_CLIPPING_RATIO = 0.02


def validate_sample(path: str) -> dict[str, Any]:
    """Return a pass/fail report with actionable reasons."""
    analysis = analyze_file(path)
    checks: list[dict[str, Any]] = []
    ok = True

    def _check(name: str, passed: bool, detail: str) -> None:
        nonlocal ok
        if not passed:
            ok = False
        checks.append({"check": name, "passed": passed, "detail": detail})

    duration = analysis["duration"]
    _check("duration", MIN_DURATION <= duration <= MAX_DURATION,
           f"{duration:.1f}s (need {MIN_DURATION}-{MAX_DURATION}s)")
    _check("snr", analysis["snr_db"] >= MIN_SNR, f"SNR {analysis['snr_db']:.1f} dB (need ≥{MIN_SNR})")
    _check("clipping", not analysis["clipping"], "peaks below 0 dBFS")
    _check("voiced", analysis["f0_mean"] > 0, f"f0 {analysis['f0_mean']:.0f} Hz (voiced content)")
    _check("energy", analysis["rms"] > 0.005, f"RMS {analysis['rms']:.4f} (non-silent)")

    return {
        "passed": ok,
        "score": round(100.0 * sum(1 for c in checks if c["passed"]) / len(checks), 1),
        "checks": checks,
        "analysis": {k: v for k, v in analysis.items() if k != "file"},
    }
