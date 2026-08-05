"""Timing optimizer — improve pacing and rhythm of a timeline."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError


class TimingOptimizer:
    """Optimizes clip timing: pacing, gaps, and rhythm heuristics."""

    def __init__(self, engine: Any | None = None) -> None:
        if engine is None:
            from modules.ai_video_studio.ai_timeline.timeline_engine import get_timeline_engine

            engine = get_timeline_engine()
        self.engine = engine

    def remove_gaps(self, track: str | None = None) -> int:
        """Shift clips left to remove gaps between them. Returns clips moved."""
        clips = self.engine.clips_on(track) if track else self.engine.ordered_clips()
        clips = sorted(clips, key=lambda c: c["start"])
        moved = 0
        cursor = 0.0
        for clip in clips:
            duration = clip["end"] - clip["start"]
            if abs(clip["start"] - cursor) > 0.001:
                clip["start"] = cursor
                clip["end"] = cursor + duration
                moved += 1
            cursor = clip["end"]
        return moved

    def enforce_min_duration(self, min_duration: float) -> list[dict[str, Any]]:
        """Extend clips shorter than min_duration. Returns adjusted clips."""
        if min_duration <= 0:
            raise ValidationError("min_duration must be positive", field="min_duration")
        adjusted: list[dict[str, Any]] = []
        for clip in self.engine.clips:
            duration = clip["end"] - clip["start"]
            if duration < min_duration:
                clip["end"] = clip["start"] + min_duration
                adjusted.append(clip)
        return adjusted

    def enforce_max_duration(self, max_duration: float) -> list[dict[str, Any]]:
        """Trim clips longer than max_duration. Returns adjusted clips."""
        if max_duration <= 0:
            raise ValidationError("max_duration must be positive", field="max_duration")
        adjusted: list[dict[str, Any]] = []
        for clip in self.engine.clips:
            duration = clip["end"] - clip["start"]
            if duration > max_duration:
                clip["end"] = clip["start"] + max_duration
                adjusted.append(clip)
        return adjusted

    def normalize_to_duration(self, target: float) -> dict[str, Any]:
        """Scale all clip durations proportionally to hit a target total."""
        if target <= 0:
            raise ValidationError("target must be positive", field="target")
        current = self.engine.duration()
        if current <= 0:
            return {"target": target, "current": 0.0, "scale": 0.0, "clips": []}
        scale = target / current
        for clip in self.engine.clips:
            duration = clip["end"] - clip["start"]
            clip["end"] = clip["start"] + duration * scale
        return {"target": target, "current": self.engine.duration(), "scale": scale, "clips": self.engine.clips}

    def suggest_pacing(self) -> dict[str, Any]:
        """Return pacing heuristics for the current timeline."""
        clips = self.engine.ordered_clips()
        if not clips:
            return {"clip_count": 0, "avg_duration": 0.0, "total": 0.0, "suggestion": "empty"}
        durations = [c["end"] - c["start"] for c in clips]
        avg = sum(durations) / len(durations)
        total = self.engine.duration()
        suggestion = "balanced"
        if avg < 2.0:
            suggestion = "too_fast"
        elif avg > 10.0:
            suggestion = "too_slow"
        return {
            "clip_count": len(clips),
            "avg_duration": round(avg, 3),
            "total": round(total, 3),
            "suggestion": suggestion,
        }


_timing_optimizer: TimingOptimizer | None = None


def get_timing_optimizer() -> TimingOptimizer:
    global _timing_optimizer
    if _timing_optimizer is None:
        _timing_optimizer = TimingOptimizer()
    return _timing_optimizer
