"""Transition track manager — transitions between adjacent clips.

A transition requires two clips that are neighbours on the same track and a
positive duration; the manager validates adjacency and exposes the dissolve
factor used by renderers to blend the two clips across the transition window.
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.transitions")

SUPPORTED = {"cut", "dissolve", "fade_black", "fade_white", "wipe_left", "wipe_right"}


class TransitionTrackManager:
    def __init__(self, timeline: Any) -> None:
        self.timeline = timeline

    def add(self, clip_a_id: str, clip_b_id: str, name: str, duration: float) -> dict[str, Any]:
        if name not in SUPPORTED:
            raise ValidationError(
                f"Unsupported transition '{name}' (expected one of {sorted(SUPPORTED)})", field="transition"
            )
        a = self.timeline.get_clip(clip_a_id)
        b = self.timeline.get_clip(clip_b_id)
        if a.get("track") != b.get("track"):
            raise ValidationError("Transitions require clips on the same track", field="transition")
        if abs(a["end"] - b["start"]) > 1e-6:
            raise ValidationError("Transitions require adjacent clips", field="transition")
        if duration <= 0:
            raise ValidationError("Transition duration must be positive", field="duration")
        return self.timeline.set_transition(clip_a_id, clip_b_id, name, duration)

    def dissolve_factor(self, transition: dict[str, Any], time: float) -> float:
        """0 → clip A fully visible, 1 → clip B fully visible (linear)."""
        clip_a = self.timeline.get_clip(transition["a"])
        start = clip_a["end"] - transition["duration"]
        if time <= start:
            return 0.0
        if time >= clip_a["end"]:
            return 1.0
        return (time - start) / transition["duration"]

    def active_transition_at(self, time: float) -> dict[str, Any] | None:
        for t in self.timeline.transitions:
            clip_a = self.timeline.get_clip(t["a"])
            if clip_a["end"] - t["duration"] <= time <= clip_a["end"]:
                return t
        return None
