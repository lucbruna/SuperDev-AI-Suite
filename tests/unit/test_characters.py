"""Tests for DARKSTUDIO's reusable character primitive library."""
from __future__ import annotations

import numpy as np
import pytest

from modules.ai_video_studio.media.canvas import SceneCanvas
from modules.ai_video_studio.media.characters import add_character, character_primitives


def test_character_identity_and_geometry_are_deterministic() -> None:
    a = character_primitives("whymentary_host", x=160, y=300)
    b = character_primitives("whymentary_host", x=160, y=300)
    assert a == b
    assert len(a["rects"]) == 2
    assert len(a["circles"]) >= 5
    assert len(a["lines"]) >= 6


def test_pose_and_expression_change_appearance_data() -> None:
    neutral = character_primitives("whymentary_host", x=160, y=300)
    expressive = character_primitives(
        "whymentary_host", x=160, y=300, pose="point", expression="surprised"
    )
    assert neutral["lines"] != expressive["lines"]
    assert neutral["circles"] != expressive["circles"]


def test_scale_scales_character_proportionally() -> None:
    small = character_primitives("historical_narrator", x=100, y=300, scale=0.5)
    large = character_primitives("historical_narrator", x=100, y=300, scale=2)
    assert large["rects"][0]["w"] == pytest.approx(small["rects"][0]["w"] * 4)


def test_invalid_character_pose_expression_and_scale_fail_fast() -> None:
    with pytest.raises(ValueError, match="Unknown character"):
        character_primitives("not_registered", x=0, y=0)
    with pytest.raises(ValueError, match="Unknown pose"):
        character_primitives("whymentary_host", x=0, y=0, pose="running")
    with pytest.raises(ValueError, match="Unknown expression"):
        character_primitives("whymentary_host", x=0, y=0, expression="angry")
    with pytest.raises(ValueError, match="scale"):
        character_primitives("whymentary_host", x=0, y=0, scale=0)


def test_add_character_integrates_with_scene_canvas_without_mutation() -> None:
    original = {
        "background_type": "solid",
        "background_colors": ["#FFFFFF"],
        "rects": [{"x": 5, "y": 5, "w": 10, "h": 10, "color": "#FF0000"}],
    }
    scene = add_character(
        original, "whymentary_host", x=160, y=190, pose="explain", expression="happy"
    )
    assert len(scene["rects"]) == 3
    assert len(scene["circles"]) >= 5
    assert len(original["rects"]) == 1
    frame = SceneCanvas(width=320, height=240).render_scene(scene, 0)
    assert frame.shape == (240, 320, 3)
    assert frame.dtype == np.uint8
    assert np.unique(frame.reshape(-1, 3), axis=0).shape[0] > 4
