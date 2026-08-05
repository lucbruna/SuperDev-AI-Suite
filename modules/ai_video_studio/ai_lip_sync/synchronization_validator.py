"""Synchronization Validator — checks timeline integrity and coverage."""
from __future__ import annotations

from typing import Any

MIN_FRAME_SPAN = 0.03
MAX_FRAME_SPAN = 0.08


def validate_timeline(timeline: list[dict[str, Any]], *, expected_fps: int = 24,
                      audio_duration: float | None = None) -> dict[str, Any]:
    """Return a report with issues found in a per-frame timeline."""
    checks: list[dict[str, Any]] = []
    ok = True

    def _check(name: str, passed: bool, detail: str) -> None:
        nonlocal ok
        if not passed:
            ok = False
        checks.append({"check": name, "passed": passed, "detail": detail})

    if not timeline:
        _check("non_empty", False, "timeline has no frames")
        return {"passed": False, "checks": checks}

    _check("non_empty", True, f"{len(timeline)} frames")

    # Frame rate sanity: consecutive frame times should be ~1/fps apart.
    spans = [b["time"] - a["time"] for a, b in zip(timeline[:-1], timeline[1:], strict=False)]
    if spans:
        expected = 1.0 / max(expected_fps, 1)
        outliers = [s for s in spans if s > expected * 2 + 0.05 or s < 0]
        _check("frame_rate", len(outliers) <= max(2, len(spans) * 0.05),
               f"{len(outliers)} frame gaps outside ±2x the expected {expected:.3f}s")

    # Coverage: mouth is closed the vast majority of the time.
    open_frames = sum(1 for f in timeline if (f.get("open") or 0.0) > 0.4)
    ratio = open_frames / len(timeline)
    _check("mouth_movement", ratio < 0.8, f"mouth open {ratio:.0%} of frames (≤80%)")

    if audio_duration:
        last = timeline[-1]["time"]
        _check("duration_coverage", abs(last - audio_duration) < max(0.5, audio_duration * 0.1),
               f"timeline {last:.2f}s vs audio {audio_duration:.2f}s")

    return {"passed": ok, "score": round(100 * sum(1 for c in checks if c["passed"]) / max(1, len(checks)), 1),
            "checks": checks}
