"""Marker manager — markers, labels, colors and markers in a range."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.markers")


class MarkerManager:
    def __init__(self, timeline: Any) -> None:
        self.timeline = timeline

    def add(self, time: float, label: str = "", color: str = "yellow") -> dict[str, Any]:
        return self.timeline.add_marker(time, label=label, color=color)

    def remove(self, marker_id: str) -> bool:
        before = len(self.timeline.markers)
        self.timeline.markers = [m for m in self.timeline.markers if m.get("id") != marker_id]
        return len(self.timeline.markers) != before

    def markers_in_range(self, start: float, end: float) -> list[dict[str, Any]]:
        return [m for m in self.timeline.markers if start <= m["time"] <= end]

    def nearest(self, time: float) -> dict[str, Any] | None:
        if not self.timeline.markers:
            return None
        return min(self.timeline.markers, key=lambda m: abs(m["time"] - time))

    def labeled(self, color: str | None = None) -> list[dict[str, Any]]:
        markers = self.timeline.markers
        if color:
            markers = [m for m in markers if m.get("color") == color]
        return list(markers)
