"""Editor optimizer — chooses preview and render parameters.

Decides whether to render with proxies, at what resolution and with which
frame skip, based on timeline duration/complexity and optional hardware hints
(cpu_count, has_gpu). Mirrors the timeline optimizer but at editor scope.
"""
from __future__ import annotations

import os
from typing import Any

from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.optimizer")


class EditorOptimizer:
    def __init__(self, *, cpu_count: int | None = None, has_gpu: bool = False) -> None:
        self.cpu_count = cpu_count or os.cpu_count() or 4
        self.has_gpu = bool(has_gpu)

    def plan(self, duration_seconds: float, clip_count: int, effect_count: int = 0) -> dict[str, Any]:
        """A render plan for a timeline with the given characteristics."""
        complexity = clip_count * 2 + effect_count * 3
        long_video = duration_seconds > 300
        heavy = complexity > 80
        use_proxy = long_video or (heavy and self.cpu_count < 8)
        if self.has_gpu:
            resolution = (3840, 2160) if not use_proxy else (1920, 1080)
        elif use_proxy:
            resolution = (1280, 720)
        else:
            resolution = (1920, 1080)
        return {
            "resolution": resolution,
            "use_proxy": use_proxy,
            "parallel_chunks": min(4, max(1, self.cpu_count // 2)),
            "frame_skip_preview": 2 if use_proxy else 1,
            "estimated_render_seconds": duration_seconds * 24 * resolution[0] * resolution[1] * (0.35 / 1_000_000),
        }
