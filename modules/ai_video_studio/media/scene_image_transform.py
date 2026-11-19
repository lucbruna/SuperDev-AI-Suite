"""Validated per-scene background image framing transforms."""
from __future__ import annotations

from math import isfinite
from typing import Any

DEFAULT_SCENE_IMAGE_TRANSFORM = {"scale": 1.0, "offset_x": 0.0, "offset_y": 0.0}


def normalize_scene_image_transform(value: Any) -> dict[str, float]:
    """Validate and normalize scale/offset controls stored with a scene."""
    if value is None:
        return dict(DEFAULT_SCENE_IMAGE_TRANSFORM)
    if not isinstance(value, dict):
        raise ValueError("background_image_transform must be an object")
    result: dict[str, float] = {}
    for key, default, minimum, maximum in (
        ("scale", 1.0, 1.0, 3.0),
        ("offset_x", 0.0, -1.0, 1.0),
        ("offset_y", 0.0, -1.0, 1.0),
    ):
        raw = value.get(key, default)
        if isinstance(raw, bool):
            raise ValueError(f"{key} must be a finite number")
        try:
            number = float(raw)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"{key} must be a finite number") from exc
        if not isfinite(number) or not minimum <= number <= maximum:
            raise ValueError(f"{key} must be between {minimum} and {maximum}")
        result[key] = number
    return result


def calculate_cover_crop(source_width: int, source_height: int, target_width: int,
                         target_height: int, transform: Any = None) -> tuple[int, int, int, int]:
    """Return a bounded crop box after cover-fit and user framing adjustments."""
    if min(source_width, source_height, target_width, target_height) <= 0:
        raise ValueError("Image and target dimensions must be positive")
    settings = normalize_scene_image_transform(transform)
    cover = max(target_width / source_width, target_height / source_height)
    scale = cover * settings["scale"]
    width = min(source_width, max(1, int(round(target_width / scale))))
    height = min(source_height, max(1, int(round(target_height / scale))))
    max_left, max_top = source_width - width, source_height - height
    left = int(round(max_left * (settings["offset_x"] + 1.0) / 2.0))
    top = int(round(max_top * (settings["offset_y"] + 1.0) / 2.0))
    left, top = min(max(0, left), max_left), min(max(0, top), max_top)
    return left, top, left + width, top + height
