"""Integration tests for studio profile application in the shared renderer."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media import render


def test_multi_scene_renderer_applies_selected_studio_profile(monkeypatch, tmp_path) -> None:
    captured: list[dict] = []

    def fake_render_scene(self, scene, frame_index):
        captured.append(scene)
        return np.zeros((16, 16, 3), dtype=np.uint8)

    def fake_stream_frames_to_video(frames, output_path, **kwargs):
        next(frames)
        return {"engine": "test", "frames": kwargs["total_frames"]}

    monkeypatch.setattr(render.SceneCanvas, "render_scene", fake_render_scene)
    monkeypatch.setattr(render, "stream_frames_to_video", fake_stream_frames_to_video)

    result = render.render_multi_scene_video(
        [
            {
                "duration": 1,
                "background_type": "radial",
                "background_colors": ["#000000", "#111111"],
                "text": {"content": "Por que isso acontece?"},
            }
        ],
        tmp_path / "profile.mp4",
        fps=1,
        width=16,
        height=16,
        studio_id="whymentary",
    )

    assert result["engine"] == "test"
    assert captured[0]["studio_id"] == "whymentary"
    assert captured[0]["background_type"] == "solid"
    assert captured[0]["background_colors"] == ["#FFFFFF"]
    assert captured[0]["text"]["content"] == "Por que isso acontece?"



def test_multi_scene_renderer_expands_narration_character_performance(monkeypatch, tmp_path) -> None:
    captured: list[dict] = []

    def fake_render_scene(self, scene, frame_index):
        captured.append(scene)
        return np.zeros((16, 16, 3), dtype=np.uint8)

    def fake_stream_frames_to_video(frames, output_path, **kwargs):
        next(frames)
        return {"engine": "test", "frames": kwargs["total_frames"]}

    monkeypatch.setattr(render.SceneCanvas, "render_scene", fake_render_scene)
    monkeypatch.setattr(render, "stream_frames_to_video", fake_stream_frames_to_video)

    result = render.render_multi_scene_video(
        [
            {
                "duration": 3,
                "background_type": "solid",
                "background_colors": ["#FFFFFF"],
                "character_performances": [
                    {
                        "character_id": "historical_narrator",
                        "narration_clip": {"start": 0, "end": 3},
                        "cues": [
                            {"offset_seconds": 1, "pose": "point", "expression": "surprised"}
                        ],
                        "x": 80,
                        "y": 175,
                        "scale": 0.5,
                    }
                ],
            }
        ],
        tmp_path / "performance.mp4",
        fps=10,
        width=16,
        height=16,
    )

    assert result["frames"] == 30
    assert "character_performances" not in captured[0]
    assert any(item.get("visible_from_frame") == 10 for item in captured[0]["lines"])
    assert any(item.get("visible_until_frame") == 10 for item in captured[0]["lines"])
