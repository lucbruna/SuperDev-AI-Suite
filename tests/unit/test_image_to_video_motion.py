from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.ai_video_generator.image_to_video.image_to_video_engine import (
    ImageToVideoEngine,
)


def test_image_to_video_motion_presets_produce_rgb_frames(tmp_path):
    source = tmp_path / "reference.png"
    pixels = np.zeros((80, 120, 3), dtype=np.uint8)
    pixels[:, :60] = (240, 30, 30)
    pixels[:, 60:] = (20, 40, 230)
    Image.fromarray(pixels).save(source)

    engine = ImageToVideoEngine()
    for preset in sorted(engine.MOTION_PRESETS):
        frames = list(engine._iter_frames(str(source), preset, 3, 12, 64, 48))
        assert len(frames) == 3
        assert all(frame.shape == (48, 64, 3) for frame in frames)
        assert all(frame.dtype == np.uint8 for frame in frames)


def test_image_to_video_streams_exact_frame_budget_and_requires_mp4(tmp_path, monkeypatch):
    source = tmp_path / "reference.png"
    Image.new("RGB", (64, 64), (80, 120, 160)).save(source)
    captured = {}

    def fake_stream(frames, output, **kwargs):
        captured["frames"] = list(frames)
        captured["output"] = output
        captured["kwargs"] = kwargs
        return {
            "output_path": str(output),
            "frames": kwargs["total_frames"],
            "bytes": 123,
            "engine": "ffmpeg",
        }

    monkeypatch.setattr(
        "modules.ai_video_studio.ai_video_generator.image_to_video.image_to_video_engine.stream_frames_to_video",
        fake_stream,
    )
    monkeypatch.setattr(
        "modules.ai_video_studio.ai_video_generator.image_to_video.image_to_video_engine.get_subsystem_dir",
        lambda _name: tmp_path,
    )
    monkeypatch.setattr(
        "modules.ai_video_studio.ai_video_generator.image_to_video.image_to_video_engine.unique_filename",
        lambda *_args: tmp_path / "generated.mp4",
    )

    result = ImageToVideoEngine().generate({
        "id": "motion-test",
        "prompt": str(source),
        "params": {"duration": 2, "fps": 5, "width": 64, "height": 64, "camera_motion": "push_in"},
    })

    assert result["frames"] == 10
    assert len(captured["frames"]) == 10
    assert captured["kwargs"]["total_frames"] == 10
    assert captured["kwargs"]["require_mp4"] is True


def test_image_to_video_rejects_unknown_motion_preset():
    with pytest.raises(ValidationError, match="Unsupported camera_motion"):
        ImageToVideoEngine().generate({
            "id": "invalid-motion",
            "prompt": "reference.png",
            "params": {"camera_motion": "teleport"},
        })
