"""Tests for reusable DARKSTUDIO procedural character assets."""
from __future__ import annotations

import pytest

from modules.ai_video_studio.media.characters import (
    add_character_to_scene,
    build_character,
)


def test_character_has_canvas_primitives_and_stable_anchor() -> None:
    first = build_character("whymentary_explainer", x=320, y=600)
    second = build_character("whymentary_explainer", x=320, y=600)
    assert first == second
    assert first["x"] == 320
    assert first["y"] == 600
    assert first["rects"] and first["circles"] and first["lines"]


def test_pose_and_expression_change_character_primitives() -> None:
    neutral = build_character("whymentary_explainer", x=100, y=300)
    pointing = build_character(
        "whymentary_explainer", x=100, y=300, pose="point", expression="surprised"
    )
    assert neutral["lines"] != pointing["lines"]
    assert neutral["circles"] != pointing["circles"]


def test_scale_changes_character_geometry() -> None:
    small = build_character("historical_narrator", x=100, y=300, scale=0.5)
    large = build_character("historical_narrator", x=100, y=300, scale=2)
    assert large["rects"][0]["w"] == small["rects"][0]["w"] * 4


def test_unknown_character_pose_expression_and_scale_are_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown character"):
        build_character("missing", x=0, y=0)
    with pytest.raises(ValueError, match="Unknown pose"):
        build_character("whymentary_explainer", x=0, y=0, pose="run")
    with pytest.raises(ValueError, match="Unknown expression"):
        build_character("whymentary_explainer", x=0, y=0, expression="angry")
    with pytest.raises(ValueError, match="scale"):
        build_character("whymentary_explainer", x=0, y=0, scale=0)


def test_add_character_to_scene_preserves_existing_content() -> None:
    source = {"rects": [{"x": 1, "y": 2, "w": 3, "h": 4}], "text": {"content": "Olá"}}
    result = add_character_to_scene(
        source, "whymentary_explainer", x=200, y=500, pose="explain"
    )
    assert len(result["rects"]) == 3
    assert result["text"] == source["text"]
    assert len(result["circles"]) > 0
    assert source == {"rects": [{"x": 1, "y": 2, "w": 3, "h": 4}], "text": {"content": "Olá"}}
