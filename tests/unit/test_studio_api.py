"""Contract tests for the DARKSTUDIO studio profile API."""
from __future__ import annotations

import asyncio

import pytest
from fastapi import HTTPException

from modules.ai_video_studio.api.routes.studios import (
    get_studio,
    list_studios,
    preview_scene_profile,
)


def test_list_studios_exposes_both_distinct_profiles() -> None:
    result = asyncio.run(list_studios())
    assert result["count"] == 2
    profiles = {item["id"]: item for item in result["studios"]}
    assert set(profiles) == {"whymentary", "historical_documentary"}
    assert profiles["whymentary"]["background"]["type"] == "solid"
    assert profiles["whymentary"]["background"]["colors"] == ["#FFFFFF"]
    assert profiles["historical_documentary"]["background"]["type"] == "gradient"


def test_get_studio_returns_serializable_visual_contract() -> None:
    result = asyncio.run(get_studio("whymentary"))
    assert result["name"] == "Whymentary"
    assert result["text"]["default_color"] == "#111827"
    assert result["camera_defaults"]["zoom"] == 1.0


def test_get_unknown_studio_returns_not_found() -> None:
    with pytest.raises(HTTPException) as error:
        asyncio.run(get_studio("unknown"))
    assert error.value.status_code == 404


def test_scene_preview_applies_profile_without_mutating_input() -> None:
    source = {
        "background_type": "radial",
        "background_colors": ["#000000", "#FFFFFF"],
        "text": {"content": "A ideia inesperada"},
    }
    result = asyncio.run(preview_scene_profile("whymentary", source))
    assert result["studio_id"] == "whymentary"
    assert result["scene"]["background_type"] == "solid"
    assert result["scene"]["background_colors"] == ["#FFFFFF"]
    assert result["scene"]["text"]["content"] == "A ideia inesperada"
    assert source["background_type"] == "radial"


def test_scene_preview_rejects_unknown_studio() -> None:
    with pytest.raises(HTTPException) as error:
        asyncio.run(preview_scene_profile("unknown", {"text": {"content": "x"}}))
    assert error.value.status_code == 404
