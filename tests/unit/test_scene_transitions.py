"""Tests for real scene-to-scene transition rendering."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import render as render_module
from modules.ai_video_studio.media.transitions import blend_frames, fade_from_black, fade_to_black


def _solid_scene(color: str, transition: dict | None = None) -> dict:
    scene = {"duration": 1.0, "background_type": "solid", "background_colors": [color]}
    if transition is not None:
        scene["transition_out"] = transition
    return scene


def test_transition_primitives_blend_and_fade_correctly() -> None:
    red = np.full((2, 2, 3), (255, 0, 0), dtype=np.uint8)
    blue = np.full((2, 2, 3), (0, 0, 255), dtype=np.uint8)
    assert tuple(blend_frames(red, blue, 0.5)[0, 0]) == (128, 0, 128)
    assert tuple(fade_to_black(red, 1.0)[0, 0]) == (0, 0, 0)
    assert tuple(fade_from_black(blue, 0.0)[0, 0]) == (0, 0, 0)
    assert tuple(fade_from_black(blue, 1.0)[0, 0]) == (0, 0, 255)


def test_multi_scene_crossfade_overlaps_frames_and_reports_shorter_duration(monkeypatch) -> None:
    captured = {}

    def fake_stream(frame_iter, output_path, **kwargs):
        frames = list(frame_iter)
        captured["frames"] = frames
        captured["kwargs"] = kwargs
        return {"output_path": str(output_path), "frames": len(frames), "fps": kwargs["fps"], "bytes": 1, "engine": "test"}

    monkeypatch.setattr(render_module, "stream_frames_to_video", fake_stream)
    result = render_module.render_multi_scene_video(
        [
            _solid_scene("#FF0000", {"type": "crossfade", "duration_frames": 2}),
            _solid_scene("#0000FF"),
        ],
        "unused.mp4", fps=4, width=4, height=4,
    )
    frames = captured["frames"]
    assert result["frames"] == 6
    assert len(frames) == 6
    assert tuple(frames[2][0, 0]) == (128, 0, 128)
    assert tuple(frames[3][0, 0]) == (0, 0, 255)


def test_fade_through_black_preserves_scene_frame_count(monkeypatch) -> None:
    captured = {}

    def fake_stream(frame_iter, output_path, **kwargs):
        frames = list(frame_iter)
        captured["frames"] = frames
        return {"output_path": str(output_path), "frames": len(frames), "fps": kwargs["fps"], "bytes": 1, "engine": "test"}

    monkeypatch.setattr(render_module, "stream_frames_to_video", fake_stream)
    render_module.render_multi_scene_video(
        [
            _solid_scene("#FF0000", {"type": "fade_through_black", "duration_frames": 2}),
            _solid_scene("#0000FF"),
        ],
        "unused.mp4", fps=4, width=4, height=4,
    )
    frames = captured["frames"]
    assert len(frames) == 8
    assert tuple(frames[3][0, 0]) == (0, 0, 0)
    assert tuple(frames[4][0, 0]) == (0, 0, 0)
    assert tuple(frames[5][0, 0]) == (0, 0, 255)


def test_invalid_transition_and_final_crossfade_are_rejected(monkeypatch) -> None:
    def fake_stream(frame_iter, output_path, **kwargs):
        list(frame_iter)
        return {"output_path": str(output_path), "frames": 1, "fps": kwargs["fps"], "bytes": 1, "engine": "test"}

    monkeypatch.setattr(render_module, "stream_frames_to_video", fake_stream)
    import pytest
    with pytest.raises(ValueError, match="Unsupported transition"):
        render_module.render_multi_scene_video([_solid_scene("#FFFFFF", {"type": "wipe"})], "x.mp4", fps=4, width=4, height=4)
    with pytest.raises(ValueError, match="final scene"):
        render_module.render_multi_scene_video([_solid_scene("#FFFFFF", {"type": "crossfade", "duration_frames": 2})], "x.mp4", fps=4, width=4, height=4)
