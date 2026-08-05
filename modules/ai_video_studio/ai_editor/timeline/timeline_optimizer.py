"""Timeline optimizer — decides proxy quality and preview strategy.

Given the timeline's clip count, duration and complexity (effects/transitions),
the optimizer recommends a preview resolution, a frame-skip rate and whether a
proxy render is worth it. Keeps the editor responsive on long timelines.
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.optimizer")

_RESOLUTIONS = [(1920, 1080), (1280, 720), (854, 480), (640, 360)]


class TimelineOptimizer:
    def __init__(self, timeline: Any) -> None:
        self.timeline = timeline

    def complexity(self) -> int:
        effects = sum(len(c.get("effects", [])) for c in self.timeline.clips)
        transitions = len(self.timeline.transitions)
        return len(self.timeline.clips) * 2 + effects * 3 + transitions * 4

    def suggest_preview(self) -> dict[str, Any]:
        """Preview settings: width/height, frame skip, use_proxy."""
        duration = self.timeline.duration()
        complexity = self.complexity()
        heavy = duration > 180 or complexity > 60
        width, height = _RESOLUTIONS[1] if heavy else _RESOLUTIONS[0]
        return {
            "width": width,
            "height": height,
            "frame_skip": 1 if not heavy else 2,
            "use_proxy": heavy,
            "complexity": complexity,
            "duration_seconds": duration,
        }

    def should_build_proxy(self, source_width: int, source_height: int) -> bool:
        """Proxy is worth it when the source is larger than the preview target."""
        preview = self.suggest_preview()
        return (source_width * source_height) > (preview["width"] * preview["height"]) * 4

    def estimated_render_seconds(self, fps: int = 24) -> float:
        """Rough CPU render estimate (0.35s per 1M frame-pixels, as elsewhere)."""
        duration = max(0.0, self.timeline.duration())
        pixels = self.suggest_preview()["width"] * self.suggest_preview()["height"]
        return duration * fps * pixels * (0.35 / 1_000_000)
