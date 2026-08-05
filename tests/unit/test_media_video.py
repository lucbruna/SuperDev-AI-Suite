"""Unit tests for media video assembly and rendering — ffmpeg + GIF fallback.

``frames_to_video`` and ``stream_frames_to_video`` must produce a real file
with ffmpeg when available and fall back to a Pillow animated GIF otherwise.
``render_still`` must write a real PNG.
"""
from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pytest

from modules.ai_video_studio.media import render
from modules.ai_video_studio.media.video import (
    ffmpeg_available,
    frames_to_video,
    stream_frames_to_video,
)


def _frames(count: int = 8, size: int = 32) -> list[np.ndarray]:
    return [np.full((size, size, 3), i * 20, dtype=np.uint8) for i in range(count)]


def test_frames_to_video_rejects_empty() -> None:
    with pytest.raises(ValueError):
        frames_to_video([], "out.mp4")


def test_frames_to_video_rejects_mismatched_sizes(tmp_path) -> None:
    frames = [np.zeros((16, 16, 3), dtype=np.uint8), np.zeros((32, 32, 3), dtype=np.uint8)]
    with pytest.raises(ValueError):
        frames_to_video(frames, str(tmp_path / "bad.mp4"))


def test_frames_to_video_rejects_bad_fps(tmp_path) -> None:
    with pytest.raises(ValueError):
        frames_to_video(_frames(), str(tmp_path / "x.mp4"), fps=0)


@pytest.mark.skipif(not ffmpeg_available(), reason="ffmpeg not installed")
def test_frames_to_video_ffmpeg_mp4(tmp_path) -> None:
    out = tmp_path / "video.mp4"
    result = frames_to_video(_frames(12), str(out), fps=12)
    assert result["engine"] == "ffmpeg"
    assert out.exists()
    assert out.stat().st_size > 0
    assert result["frames"] == 12
    assert result["fps"] == 12


def test_frames_to_video_gif_fallback(tmp_path) -> None:
    """Without ffmpeg the pipeline must still produce a file (GIF)."""
    out = tmp_path / "video.mp4"
    with patch("modules.ai_video_studio.media.video.ffmpeg_available", return_value=False):
        result = frames_to_video(_frames(6), str(out), fps=12)
    assert result["engine"] == "pillow-gif"
    gif = tmp_path / "video.gif"
    assert gif.exists()
    assert gif.stat().st_size > 0


@pytest.mark.skipif(not ffmpeg_available(), reason="ffmpeg not installed")
def test_stream_frames_to_video_ffmpeg_mp4(tmp_path) -> None:
    """Streaming encoder must produce a real MP4 from a lazy generator."""
    out = tmp_path / "streamed.mp4"
    result = stream_frames_to_video(
        (np.full((32, 32, 3), i * 20, dtype=np.uint8) for i in range(12)),
        str(out),
        fps=12,
    )
    assert result["engine"] == "ffmpeg"
    assert out.exists()
    assert out.stat().st_size > 0
    assert result["frames"] == 12
    assert result["fps"] == 12


def test_stream_frames_to_video_rejects_empty(tmp_path) -> None:
    with pytest.raises(ValueError):
        stream_frames_to_video(iter([]), str(tmp_path / "x.mp4"), fps=12)


def test_stream_frames_to_video_rejects_mismatched_sizes(tmp_path) -> None:
    def _gen():
        yield np.zeros((16, 16, 3), dtype=np.uint8)
        yield np.zeros((32, 32, 3), dtype=np.uint8)

    with pytest.raises(ValueError):
        stream_frames_to_video(_gen(), str(tmp_path / "bad.mp4"), fps=12)


def test_stream_frames_to_video_gif_fallback(tmp_path) -> None:
    """Without ffmpeg the streaming path must still produce a GIF."""
    out = tmp_path / "video.mp4"
    with patch("modules.ai_video_studio.media.video.ffmpeg_available", return_value=False):
        result = stream_frames_to_video(
            (np.full((32, 32, 3), i * 20, dtype=np.uint8) for i in range(6)),
            str(out),
            fps=12,
        )
    assert result["engine"] == "pillow-gif"
    gif = tmp_path / "video.gif"
    assert gif.exists()
    assert gif.stat().st_size > 0


def test_render_multi_scene_streams_and_reports_total_frames(tmp_path) -> None:
    """render_multi_scene_video streams frames and reports the exact count."""
    scenes = [
        {"background_colors": ["#1a1a2e", "#0f3460"], "duration": 1.0},
        {"background_colors": ["#533483", "#e94560"], "duration": 1.5},
    ]
    result = render.render_multi_scene_video(
        scenes, tmp_path / "multi.mp4", fps=12, width=64, height=64,
    )
    # 1.0s * 12fps + 1.5s * 12fps = 12 + 18 = 30 frames
    assert result["frames"] == 30
    assert (tmp_path / "multi.mp4").exists()


def test_render_multi_scene_on_frame_reports_progress(tmp_path) -> None:
    """on_frame(rendered, total) fires once per frame, ending at 30/30."""
    scenes = [
        {"background_colors": ["#1a1a2e", "#0f3460"], "duration": 1.0},
        {"background_colors": ["#533483", "#e94560"], "duration": 1.5},
    ]
    calls: list[tuple[int, int]] = []

    def _on_frame(rendered: int, total: int) -> None:
        calls.append((rendered, total))

    render.render_multi_scene_video(
        scenes, tmp_path / "multi.mp4", fps=12, width=64, height=64,
        on_frame=_on_frame,
    )
    assert len(calls) == 30
    assert calls[0] == (1, 30)
    assert calls[-1] == (30, 30)
    # Strictly increasing, never exceeds the total.
    rendered = [c[0] for c in calls]
    assert rendered == sorted(rendered)
    assert all(t == 30 for _, t in calls)


def test_render_multi_scene_on_frame_skipped_by_default(tmp_path) -> None:
    """Without on_frame the renderer behaves exactly as before."""
    scenes = [{"background_colors": ["#1a1a2e", "#0f3460"], "duration": 0.5}]
    result = render.render_multi_scene_video(
        scenes, tmp_path / "multi.mp4", fps=12, width=64, height=64,
    )
    assert result["frames"] == 6


def test_render_multi_scene_rejects_empty() -> None:
    with pytest.raises(ValueError):
        render.render_multi_scene_video([], "out.mp4")


def test_render_still_png(tmp_path) -> None:
    scene = {
        "background_colors": ["#1a1a2e", "#0f3460"],
        "text": {"content": "Hello", "size": 40, "color": "#FFFFFF"},
        "particles": [{"x": 10, "y": 10, "vx": 0, "vy": 0, "radius": 3, "color": "#FFFFFF"}],
        "camera": {"dx": 0, "dy": 0, "zoom": 1.0},
    }
    out = render.render_still(scene, tmp_path / "still.png", width=320, height=180)
    assert out.exists()
    assert out.stat().st_size > 0
    assert out.suffix == ".png"


def test_render_still_deterministic(tmp_path) -> None:
    scene = {"background_colors": ["#112233", "#445566"]}
    a = render.render_still(scene, tmp_path / "a.png", seed=7)
    b = render.render_still(scene, tmp_path / "b.png", seed=7)
    assert a.read_bytes() == b.read_bytes()
