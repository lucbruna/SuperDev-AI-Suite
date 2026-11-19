from __future__ import annotations

import pytest

from modules.ai_video_studio.media.scene_image_transform import calculate_cover_crop, normalize_scene_image_transform


def test_default_transform_preserves_centered_cover_crop() -> None:
    assert normalize_scene_image_transform(None) == {"scale": 1.0, "offset_x": 0.0, "offset_y": 0.0}
    assert calculate_cover_crop(1920, 1080, 1280, 720) == (0, 0, 1920, 1080)


def test_scale_and_offsets_change_crop_within_source_bounds() -> None:
    left_top = calculate_cover_crop(2400, 1600, 1280, 720, {"scale": 1.8, "offset_x": -1, "offset_y": -1})
    right_bottom = calculate_cover_crop(2400, 1600, 1280, 720, {"scale": 1.8, "offset_x": 1, "offset_y": 1})
    assert left_top[:2] == (0, 0)
    assert right_bottom[2:] == (2400, 1600)
    assert left_top != right_bottom


@pytest.mark.parametrize("value", [
    {"scale": 0.5}, {"scale": 3.1}, {"offset_x": -1.1}, {"offset_y": 1.1},
    {"scale": float("nan")}, {"scale": True}, "invalid",
])
def test_invalid_transform_is_rejected(value) -> None:
    with pytest.raises(ValueError):
        normalize_scene_image_transform(value)


def test_crop_rejects_invalid_dimensions() -> None:
    with pytest.raises(ValueError):
        calculate_cover_crop(0, 100, 100, 100)
