"""Regression tests for eased camera moves used by DARKSTUDIO."""
from __future__ import annotations

import numpy as np
import pytest

from modules.ai_video_studio.media.camera_motion import camera_state_at_frame, studio_camera_move
from modules.ai_video_studio.media.canvas import SceneCanvas


def test_camera_keyframes_interpolate_with_smooth_easing() -> None:
    camera = {
        "keyframes": [
            {"frame": 0, "dx": 0, "dy": 0, "zoom": 1.0, "roll": 0},
            {"frame": 10, "dx": 20, "dy": -10, "zoom": 1.2, "roll": 2},
        ]
    }
    assert camera_state_at_frame(camera, -1)["zoom"] == 1.0
    midpoint = camera_state_at_frame(camera, 5)
    assert midpoint == {"dx": 10.0, "dy": -5.0, "zoom": 1.1, "roll": 1.0}
    assert camera_state_at_frame(camera, 20)["dx"] == 20.0


def test_camera_keyframes_reject_non_increasing_frames_and_invalid_zoom() -> None:
    with pytest.raises(ValueError, match="strictly increasing"):
        camera_state_at_frame({"keyframes": [{"frame": 2}, {"frame": 2}]}, 2)
    with pytest.raises(ValueError, match="zoom"):
        camera_state_at_frame({"keyframes": [{"frame": 0, "zoom": 0}, {"frame": 2}]}, 1)


def test_studio_camera_presets_are_distinct_and_alternate_direction() -> None:
    historical = studio_camera_move("historical_documentary", 0, 120)
    historical_reverse = studio_camera_move("historical_documentary", 1, 120)
    explainer = studio_camera_move("whymentary", 0, 120)
    assert historical["keyframes"][-1]["zoom"] > explainer["keyframes"][-1]["zoom"]
    assert historical["keyframes"][-1]["dx"] == -historical_reverse["keyframes"][-1]["dx"]
    assert explainer["keyframes"][-1]["roll"] == 0


def test_scene_canvas_renders_camera_keyframe_motion() -> None:
    canvas = SceneCanvas(width=160, height=100, fps=24, seed=1)
    scene = {
        "background_type": "solid",
        "background_colors": ["#000000"],
        "rects": [{"x": 50, "y": 30, "w": 30, "h": 30, "color": "#FFFFFF"}],
        "camera": studio_camera_move("historical_documentary", 0, 24),
    }
    first = canvas.render_scene(scene, 0)
    last = canvas.render_scene(scene, 23)
    assert first.shape == (100, 160, 3)
    assert last.shape == (100, 160, 3)
    assert not np.array_equal(first, last)
