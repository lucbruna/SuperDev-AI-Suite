"""Tests for profile-specific canvas grading."""
from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

from modules.ai_video_studio.media.canvas import SceneCanvas


def test_zero_grading_preserves_flat_studio_colors() -> None:
    canvas = SceneCanvas(width=4, height=4)
    pixels = np.full((4, 4, 3), (20, 80, 160), dtype=np.uint8)
    original = Image.fromarray(pixels)
    result = canvas._apply_grading(original, ["#FFFFFF"], strength=0.0)
    assert np.array_equal(np.asarray(result), pixels)


def test_grading_strength_is_bounded() -> None:
    canvas = SceneCanvas(width=4, height=4)
    original = Image.new("RGB", (4, 4), (10, 20, 30))
    with pytest.raises(ValueError, match="between 0 and 1"):
        canvas._apply_grading(original, ["#FFFFFF"], strength=1.2)


def test_solid_background_preserves_single_profile_color() -> None:
    canvas = SceneCanvas(width=3, height=2)
    frame = canvas.render_scene(
        {
            "background_type": "solid",
            "background_colors": ["#FFFFFF"],
            "noise": 0.0,
            "grading_strength": 0.0,
        },
        0,
    )
    expected = np.full((2, 3, 3), 255, dtype=np.uint8)
    assert np.array_equal(frame, expected)


def test_solid_background_without_color_uses_documented_fallback() -> None:
    canvas = SceneCanvas(width=2, height=2)
    frame = canvas.render_scene(
        {"background_type": "solid", "background_colors": [], "grading_strength": 0.0},
        0,
    )
    expected = np.full((2, 2, 3), (26, 26, 46), dtype=np.uint8)
    assert np.array_equal(frame, expected)
