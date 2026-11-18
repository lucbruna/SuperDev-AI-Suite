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



def test_frames_to_video_requires_mp4_when_ffmpeg_is_missing(tmp_path) -> None:
    """DARKSTUDIO must fail rather than silently delivering a GIF as MP4."""
    out = tmp_path / "required.mp4"
    with patch("modules.ai_video_studio.media.video.ffmpeg_available", return_value=False):
        with pytest.raises(RuntimeError, match="FFmpeg is required"):
            frames_to_video(_frames(3), str(out), fps=12, require_mp4=True)
    assert not out.exists()
    assert not (tmp_path / "required.gif").exists()


def test_frames_to_video_require_mp4_rejects_other_extensions(tmp_path) -> None:
    with pytest.raises(ValueError, match="must end with .mp4"):
        frames_to_video(_frames(3), str(tmp_path / "output.gif"), require_mp4=True)


def test_stream_frames_to_video_requires_mp4_when_ffmpeg_is_missing(tmp_path) -> None:
    out = tmp_path / "required-stream.mp4"
    with patch("modules.ai_video_studio.media.video.ffmpeg_available", return_value=False):
        with pytest.raises(RuntimeError, match="FFmpeg is required"):
            stream_frames_to_video(
                (frame for frame in _frames(3)), str(out), fps=12, require_mp4=True,
            )
    assert not out.exists()
    assert not (tmp_path / "required-stream.gif").exists()


def test_render_multi_scene_can_require_mp4(tmp_path) -> None:
    scenes = [{"background_colors": ["#112233", "#445566"], "duration": 0.25}]
    with patch("modules.ai_video_studio.media.video.ffmpeg_available", return_value=False):
        with pytest.raises(RuntimeError, match="FFmpeg is required"):
            render.render_multi_scene_video(
                scenes, tmp_path / "required.mp4", fps=4, width=32, height=32,
                require_mp4=True,
            )


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



@pytest.mark.skipif(not ffmpeg_available(), reason="ffmpeg not installed")
def test_frames_to_video_require_mp4_success(tmp_path) -> None:
    """Strict mode must produce an actual MP4 when FFmpeg is available."""
    out = tmp_path / "strict.mp4"
    result = frames_to_video(_frames(12), out, fps=12, require_mp4=True)
    assert result["engine"] == "ffmpeg"
    assert result["output_path"] == str(out)
    assert out.is_file()
    assert out.stat().st_size > 0

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


@pytest.mark.skipif(not ffmpeg_available(), reason="ffmpeg not installed; MP4 output cannot be asserted")
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


def test_single_scene_clip_uses_streaming_multi_scene_renderer(monkeypatch, tmp_path):
    captured = {}
    def fake_render(scenes, output_path, **kwargs):
        captured["scenes"] = scenes
        captured["output_path"] = output_path
        captured["kwargs"] = kwargs
        return {"output_path": str(output_path), "frames": 240, "bytes": 100, "engine": "ffmpeg"}
    monkeypatch.setattr(render, "render_multi_scene_video", fake_render)
    source_scene = {"duration": 4, "transition_out": {"type": "crossfade", "duration_frames": 12}}
    result = render.render_single_scene_clip(
        source_scene, tmp_path / "clip.mp4", duration=10, fps=24,
        width=640, height=360, require_mp4=True, studio_id="whymentary",
    )
    assert captured["scenes"][0]["duration"] == 10
    assert captured["scenes"][0]["transition_out"]["type"] == "cut"
    assert captured["kwargs"]["require_mp4"] is True
    assert result["frames"] == 240
    assert source_scene["duration"] == 4


def test_mixed_scene_renderer_applies_crossfade_and_fade_through_black(monkeypatch, tmp_path):
    from pathlib import Path
    from modules.ai_video_studio.media import output_paths

    video_root = tmp_path / "videos"
    video_root.mkdir()
    sources = {}
    for index in range(3):
        source = video_root / f"generated_{index}.mp4"
        source.write_bytes(b"source")
        sources[index] = str(source)

    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: video_root)
    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/ffmpeg")
    commands = []

    class Completed:
        returncode = 0
        stderr = ""

    def fake_run(command, **kwargs):
        commands.append(command)
        Path(command[-1]).write_bytes(b"encoded")
        return Completed()

    monkeypatch.setattr("subprocess.run", fake_run)
    scenes = [
        {"duration": 2.0, "_source_scene_index": 0,
         "transition_out": {"type": "crossfade", "duration_frames": 12}},
        {"duration": 2.0, "_source_scene_index": 1,
         "transition_out": {"type": "fade_through_black", "duration_frames": 12}},
        {"duration": 2.0, "_source_scene_index": 2,
         "transition_out": {"type": "cut", "duration_frames": 0}},
    ]
    result = render.render_mixed_scene_video(
        scenes, tmp_path / "mixed.mp4", generated_clips=sources,
        fps=24, width=320, height=180,
    )

    final_command = commands[-1]
    filter_graph = final_command[final_command.index("-filter_complex") + 1]
    assert "xfade=transition=fade" in filter_graph
    assert "fade=t=out" in filter_graph
    assert "fade=t=in" in filter_graph
    assert "concat=n=2" in filter_graph
    assert result["frames"] == 132
    assert result["transition_policy"] == "frame_accurate"
    assert [item["type"] for item in result["transitions_applied"]] == [
        "crossfade", "fade_through_black",
    ]
    assert (tmp_path / "mixed.mp4").read_bytes() == b"encoded"


def test_mixed_scene_renderer_rejects_final_crossfade(monkeypatch, tmp_path):
    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/ffmpeg")
    with pytest.raises(ValueError, match="final scene"):
        render.render_mixed_scene_video(
            [{"duration": 2.0, "transition_out": {"type": "crossfade", "duration_frames": 12}}],
            tmp_path / "invalid.mp4", generated_clips={}, fps=24, width=320, height=180,
        )
