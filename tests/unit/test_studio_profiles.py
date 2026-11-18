"""Tests for independent DARKSTUDIO studio visual profiles."""
from __future__ import annotations

import pytest

from modules.ai_video_studio.media.studio_profiles import (
    HISTORICAL_DOCUMENTARY,
    WHYMENTARY,
    apply_studio_profile,
    get_studio_profile,
)


def test_two_studio_profiles_are_registered_and_distinct() -> None:
    why = get_studio_profile("whymentary")
    history = get_studio_profile("historical_documentary")
    assert why == WHYMENTARY
    assert history == HISTORICAL_DOCUMENTARY
    assert why.background_type == "solid"
    assert why.background_colors == ("#FFFFFF",)
    assert history.background_type == "gradient"
    assert history.background_colors != why.background_colors
    assert why.noise == 0.0
    assert history.noise > 0.0


def test_apply_profile_enforces_studio_visual_identity() -> None:
    source = {
        "background_type": "radial",
        "background_colors": ["#000000", "#FFFFFF"],
        "noise": 0.9,
        "text": {"content": "A ideia inesperada"},
        "rects": [{"x": 10, "y": 20, "w": 30, "h": 40, "color": "#FF0000"}],
    }
    rendered = apply_studio_profile("whymentary", source)
    assert rendered["background_type"] == "solid"
    assert rendered["background_colors"] == ["#FFFFFF"]
    assert rendered["noise"] == 0.0
    assert rendered["text"]["content"] == "A ideia inesperada"
    assert rendered["text"]["color"] == "#111827"
    assert rendered["rects"] == source["rects"]
    assert source["background_type"] == "radial"
    assert source["text"] == {"content": "A ideia inesperada"}


def test_historical_profile_keeps_scene_specific_camera_overrides() -> None:
    rendered = apply_studio_profile(
        "historical_documentary",
        {"camera": {"zoom": 1.12}, "text": {"content": "A queda do império"}},
    )
    assert rendered["background_type"] == "gradient"
    assert rendered["camera"]["zoom"] == 1.12
    assert rendered["camera"]["dx"] == 0.12
    assert rendered["text"]["color"] == "#F8FAFC"


def test_unknown_studio_fails_explicitly() -> None:
    with pytest.raises(ValueError, match="Unknown studio"):
        get_studio_profile("unknown")


def test_profile_application_does_not_mutate_input() -> None:
    source = {"camera": {"zoom": 1.1}, "text": {"content": "Teste"}}
    apply_studio_profile("whymentary", source)
    assert source == {"camera": {"zoom": 1.1}, "text": {"content": "Teste"}}
