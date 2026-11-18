"""High-level media helpers — render scenes to real files."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable

import numpy as np

from modules.ai_video_studio.media.canvas import SceneCanvas
from modules.ai_video_studio.media.studio_profiles import apply_studio_profile
from modules.ai_video_studio.media.video import frames_to_video, stream_frames_to_video


def _prepare_scene(scene: dict[str, Any], studio_id: str | None) -> dict[str, Any]:
    """Apply a studio visual contract when a studio is explicitly selected."""
    return apply_studio_profile(studio_id, scene) if studio_id else scene


def render_still(
    scene: dict[str, Any],
    output_path: str | Path,
    *,
    width: int = 1280,
    height: int = 720,
    seed: int = 42,
    studio_id: str | None = None,
) -> Path:
    """Render one PNG, optionally enforcing a studio visual profile."""
    canvas = SceneCanvas(width=width, height=height, seed=seed)
    frame = canvas.render_scene(_prepare_scene(scene, studio_id), 0)
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
    require_mp4: bool = False,
    studio_id: str | None = None,
) -> dict[str, Any]:
    """Render one scene, optionally enforcing a studio visual profile."""
    scene = _prepare_scene(scene, studio_id)
    canvas = SceneCanvas(width=width, height=height, fps=fps, seed=seed)
    total = max(1, int(duration * fps))
    frames: list[np.ndarray] = []
    for i in range(total):
        frames.append(canvas.render_scene(scene, i))
    return frames_to_video(frames, output_path, fps=fps, require_mp4=require_mp4)


def render_multi_scene_video(
    scenes: list[dict[str, Any]],
    output_path: str | Path,
    *,
    fps: int = 24,
    width: int = 1280,
    height: int = 720,
    seed: int = 42,
    on_frame: Callable[[int, int], None] | None = None,
    require_mp4: bool = False,
    studio_id: str | None = None,
) -> dict[str, Any]:
    """Render a storyboard into one continuous video.

    Frames are streamed to FFmpeg so long videos do not accumulate in memory.
    When studio_id is provided, its visual contract is applied to every scene.
    Scene-specific content and geometry are preserved.
    """
    canvas = SceneCanvas(width=width, height=height, fps=fps, seed=seed)
    if not scenes:
        raise ValueError("No scenes to render")
    prepared_scenes = [_prepare_scene(scene, studio_id) for scene in scenes]

    total_frames = 0
    for scene in prepared_scenes:
        duration = float(scene.get("duration", 3.0))
        total_frames += max(1, int(duration * fps))
    if total_frames <= 0:
        raise ValueError("No scenes to render")

    def _frame_iter():
        rendered = 0
        for scene in prepared_scenes:
            duration = float(scene.get("duration", 3.0))
            total = max(1, int(duration * fps))
            for i in range(total):
                yield canvas.render_scene(scene, i)
                rendered += 1
                if on_frame is not None:
                    on_frame(rendered, total_frames)

    return stream_frames_to_video(
        _frame_iter(),
        output_path,
        fps=fps,
        total_frames=total_frames,
        require_mp4=require_mp4,
    )


def render_sim_frames(
    make_frame: Callable[[int], np.ndarray],
    output_path: str | Path,
    *,
    frames: int = 60,
    fps: int = 24,
    require_mp4: bool = False,
) -> dict[str, Any]:
    """Render video from an arbitrary frame callback."""
    rendered: list[np.ndarray] = []
    for i in range(frames):
        frame = make_frame(i)
        if frame is None:
            continue
        rendered.append(np.asarray(frame, dtype=np.uint8))
    if not rendered:
        raise ValueError("Frame callback produced no frames")
    return frames_to_video(rendered, output_path, fps=fps, require_mp4=require_mp4)


def timeit(fn: Callable[[], Any]) -> tuple[Any, float]:
    """Run a callable and return (result, elapsed_seconds)."""
    started = time.time()
    result = fn()
    return result, round(time.time() - started, 3)
