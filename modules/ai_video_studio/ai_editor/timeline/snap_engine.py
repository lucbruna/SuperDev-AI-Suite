"""Snap engine — magnetism for the playhead and clip edges.

``snap(time, radius)`` returns the nearest snap candidate (clip in/out edges,
markers, subtitles, zero) within ``radius`` seconds, otherwise returns the
original time untouched. This powers the "magnetic" feel of the editor.
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.snap")


class SnapEngine:
    def __init__(self, timeline: Any) -> None:
        self.timeline = timeline

    def candidates(self) -> list[float]:
        """All snap points on the timeline (unique, sorted)."""
        points = {0.0}
        for clip in self.timeline.clips:
            points.add(float(clip["start"]))
            points.add(float(clip["end"]))
        for marker in self.timeline.markers:
            points.add(float(marker["time"]))
        for cue in self.timeline.subtitles:
            points.add(float(cue["start"]))
            points.add(float(cue["end"]))
        return sorted(points)

    def snap(self, time: float, radius: float = 0.5) -> float:
        """Return ``time`` snapped to the nearest candidate within ``radius``."""
        best, best_dist = time, radius
        for point in self.candidates():
            dist = abs(point - time)
            if dist <= best_dist:
                best, best_dist = point, dist
        return best
