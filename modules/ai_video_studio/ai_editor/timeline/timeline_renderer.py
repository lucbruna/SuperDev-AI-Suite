"""Timeline renderer — turns the timeline model into real video.

Frames are produced by compositing the active video clips at each time: clips
render their ``frame`` provider (a callable or static array in ``frame``) into
a canvas respecting opacity and transform, then the frames are encoded to an
MP4/GIF through the shared ``media.video`` toolkit (FFmpeg, GIF fallback).
Subtitles and markers are drawn on top for preview completeness.
"""
from __future__ import annotations

from typing import Any, Callable

import numpy as np

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.editor_common import as_rgb, make_logger, resize_frame

logger = make_logger("editor.renderer")


class TimelineRenderer:
    """Composites timeline clips into frames and encodes a video."""

    def __init__(self, timeline: Any, *, width: int = 1280, height: int = 720) -> None:
        self.timeline = timeline
        self.width = width
        self.height = height

    def _canvas(self) -> np.ndarray:
        return np.zeros((self.height, self.width, 3), dtype=np.uint8)

    def _clip_frame(self, clip: dict[str, Any], time: float) -> np.ndarray | None:
        """Return the clip's pixels at ``time`` (None when it has no frame)."""
        provider = clip.get("frame")
        if provider is None:
            return None
        local = time - clip["start"]
        if isinstance(provider, np.ndarray):
            idx = min(int(local * (self.timeline.fps or 24)), provider.shape[0] - 1)
            frame = provider[idx]
        elif callable(provider):
            frame = provider(local)
        else:
            return None
        frame = resize_frame(frame, self.width, self.height).astype(np.float32)
        opacity = float(clip.get("opacity", 1.0))
        if opacity < 1.0:
            frame *= opacity
        tf = clip.get("transform") or {}
        scale = float(tf.get("scale", 1.0))
        if scale != 1.0:
            frame = resize_frame(frame.astype(np.uint8),
                                 max(1, int(self.width * scale)), max(1, int(self.height * scale))).astype(np.float32)
        return frame

    def frame_at(self, time: float, width: int | None = None, height: int | None = None) -> np.ndarray:
        """Composite the video clips active at ``time`` into one frame."""
        w, h = width or self.width, height or self.height
        canvas = np.zeros((h, w, 3), dtype=np.float32)
        for clip in self.timeline.clips_at(time):
            frame = self._clip_frame(clip, time)
            if frame is None:
                continue
            th, tw = frame.shape[:2]
            y0, x0 = (h - th) // 2, (w - tw) // 2
            canvas[y0:y0 + th, x0:x0 + tw] += frame
        canvas = np.clip(canvas, 0, 255).astype(np.uint8)
        text = self.timeline.subtitle_at(time)
        if text:
            canvas = self._draw_subtitle(canvas, text)
        return canvas

    def render(
        self,
        output_path: str,
        *,
        fps: int = 24,
        width: int | None = None,
        height: int | None = None,
        progress: bool = True,
    ) -> dict[str, Any]:
        """Render the whole timeline and encode it to a real file."""
        from modules.ai_video_studio.media import video as media_video

        w = width or self.width
        h = height or self.height
        duration = self.timeline.duration()
        if duration <= 0:
            raise ValidationError("Timeline is empty — nothing to render", field="timeline")
        total = max(1, int(duration * fps))

        def frames() -> Any:
            for i in range(total):
                t = i / fps
                if progress and i % max(1, total // 20) == 0:
                    logger.info("rendering frame %d/%d", i + 1, total)
                yield self.frame_at(t, width=w, height=h)

        result = media_video.stream_frames_to_video(
            frames(), output_path, fps=fps, total_frames=total,
        )
        result["duration_seconds"] = duration
        return result

    def _draw_subtitle(self, canvas: np.ndarray, text: str) -> np.ndarray:
        try:
            from PIL import Image, ImageDraw

            img = Image.fromarray(canvas)
            draw = ImageDraw.Draw(img)
            w, h = canvas.shape[1], canvas.shape[0]
            draw.rounded_rectangle([w // 2 - 160, h - 70, w // 2 + 160, h - 30], radius=8, fill=(0, 0, 0, 160))
            draw.text((w // 2, h - 50), text, fill=(255, 255, 255), anchor="mm")
            return np.asarray(img, dtype=np.uint8)
        except Exception:  # noqa: BLE001 — subtitles are cosmetic
            return canvas
