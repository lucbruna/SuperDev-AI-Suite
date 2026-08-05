"""High-level media helpers — render scenes to real files.

These functions hide the canvas + ffmpeg wiring so engines stay concise:

* ``render_scene_video(scene, duration, fps, out)`` — one scene → MP4.
* ``render_multi_scene_video(scenes, durations, fps, out)`` — storyboard → MP4.
* ``render_still(scene, out)`` — one scene → PNG.
* ``render_sim_frames(make_frame, frames, fps, out)`` — arbitrary frame
  generator callback → MP4 (used by animation/camera/physics).
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable

import numpy as np

from modules.ai_video_studio.media.canvas import SceneCanvas
from modules.ai_video_studio.media.video import frames_to_video, stream_frames_to_video


def render_still(scene: dict[str, Any], output_path: str | Path, *, width: int = 1280, height: int = 720, seed: int = 42) -> Path:
    """Render a single scene to a real PNG file."""
    canvas = SceneCanvas(width=width, height=height, seed=seed)
    frame = canvas.render_scene(scene, 0)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    from PIL import Image

    Image.fromarray(frame).save(out, format="PNG")
    return out


def render_scene_video(
    scene: dict[str, Any],
    output_path: str | Path,
    *,
    duration: float = 5.0,
    fps: int = 24,
    width: int = 1280,
    height: int = 720,
    seed: int = 42,
) -> dict[str, Any]:
    """Render a single scene descriptor into a real video file."""
    canvas = SceneCanvas(width=width, height=height, fps=fps, seed=seed)
    total = max(1, int(duration * fps))
    frames: list[np.ndarray] = []
    for i in range(total):
        frames.append(canvas.render_scene(scene, i))
    return frames_to_video(frames, output_path, fps=fps)


def render_multi_scene_video(
    scenes: list[dict[str, Any]],
    output_path: str | Path,
    *,
    fps: int = 24,
    width: int = 1280,
    height: int = 720,
    seed: int = 42,
    on_frame: Callable[[int, int], None] | None = None,
) -> dict[str, Any]:
    """Render a storyboard (list of scenes) into one continuous video.

    Frames are streamed to FFmpeg (lazy generator) so long videos (up to
    10 minutes) never accumulate in memory.

    ``on_frame(rendered, total_frames)`` — if given, called after each frame
    is rendered/encoded so callers can surface live render progress (e.g. the
    job polling endpoint for 5–10 minute videos).
    """
    canvas = SceneCanvas(width=width, height=height, fps=fps, seed=seed)
    if not scenes:
        raise ValueError("No scenes to render")
    # Compute the exact frame budget up front (also validates durations).
    total_frames = 0
    for scene in scenes:
        duration = float(scene.get("duration", 3.0))
        total_frames += max(1, int(duration * fps))
    if total_frames <= 0:
        raise ValueError("No scenes to render")

    def _frame_iter():
        rendered = 0
        for scene in scenes:
            duration = float(scene.get("duration", 3.0))
            total = max(1, int(duration * fps))
            for i in range(total):
                yield canvas.render_scene(scene, i)
                rendered += 1
                if on_frame is not None:
                    on_frame(rendered, total_frames)

    return stream_frames_to_video(
        _frame_iter(), output_path, fps=fps, total_frames=total_frames,
    )


def render_sim_frames(
    make_frame: Callable[[int], np.ndarray],
    output_path: str | Path,
    *,
    frames: int = 60,
    fps: int = 24,
) -> dict[str, Any]:
    """Render videos from an arbitrary frame callback.

    ``make_frame(frame_index)`` must return an ``np.ndarray`` (H, W, 3).
    Used by animation, camera and physics engines.
    """
    rendered: list[np.ndarray] = []
    for i in range(frames):
        frame = make_frame(i)
        if frame is None:
            continue
        rendered.append(np.asarray(frame, dtype=np.uint8))
    if not rendered:
        raise ValueError("Frame callback produced no frames")
    return frames_to_video(rendered, output_path, fps=fps)


def timeit(fn: Callable[[], Any]) -> tuple[Any, float]:
    """Run a callable and return (result, elapsed_seconds)."""
    started = time.time()
    result = fn()
    return result, round(time.time() - started, 3)
