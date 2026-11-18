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


def test_character_catalog_keeps_mia_and_leo_identity_contracts() -> None:
    from modules.ai_video_studio.api.routes.studios import list_studio_characters

    result = asyncio.run(list_studio_characters("whymentary"))
    assert result["count"] == 2
    by_id = {item["id"]: item for item in result["characters"]}
    assert by_id["leo"]["appearance"]["hair"] == "blonde"
    assert by_id["leo"]["appearance"]["clothing_color"] == "#2563EB"
    assert by_id["mia"]["appearance"]["hair"] == "brown hair tied up"
    assert by_id["mia"]["appearance"]["outfit"] == "red dress"


def test_character_preview_returns_editable_scene_without_mutating_source() -> None:
    from modules.ai_video_studio.api.routes.studios import preview_studio_character

    source = {"background_type": "solid", "background_colors": ["#FFFFFF"]}
    result = asyncio.run(preview_studio_character(
        "mia", {"scene": source, "x": 100, "y": 200, "pose": "point"}
    ))
    assert result["character_id"] == "mia"
    assert len(result["scene"]["rects"]) == 3
    assert len(source.get("rects", [])) == 0


def test_character_preview_rejects_invalid_pose() -> None:
    from modules.ai_video_studio.api.routes.studios import preview_studio_character

    with pytest.raises(HTTPException) as error:
        asyncio.run(preview_studio_character("leo", {"scene": {}, "pose": "dance"}))
    assert error.value.status_code == 422


def test_scene_object_catalog_is_filtered_by_studio() -> None:
    from modules.ai_video_studio.api.routes.studios import list_studio_objects

    whymentary = asyncio.run(list_studio_objects("whymentary"))
    historical = asyncio.run(list_studio_objects("historical_documentary"))
    assert whymentary["count"] >= 4
    assert historical["count"] >= 4
    assert all(item["studio_id"] == "whymentary" for item in whymentary["objects"])
    assert all(item["studio_id"] == "historical_documentary" for item in historical["objects"])


def test_scene_object_preview_composes_editable_primitives_without_mutation() -> None:
    from modules.ai_video_studio.api.routes.studios import preview_scene_object

    source = {"background_type": "solid", "rects": [{"x": 1, "y": 1, "w": 2, "h": 2}]}
    result = asyncio.run(preview_scene_object(
        "water_glass", {"scene": source, "x": 100, "y": 50, "scale": 2}
    ))
    assert result["object_id"] == "water_glass"
    assert len(result["scene"]["rects"]) == 3
    assert result["scene"]["rects"][1]["x"] == 100
    assert result["scene"]["rects"][1]["y"] == 50
    assert result["scene"]["rects"][1]["motion_frames"] == 12
    assert len(source["rects"]) == 1


def test_scene_object_preview_rejects_unknown_object_and_invalid_scale() -> None:
    from modules.ai_video_studio.api.routes.studios import preview_scene_object

    with pytest.raises(HTTPException) as unknown:
        asyncio.run(preview_scene_object("not-a-prop", {"scene": {}}))
    assert unknown.value.status_code == 422

    with pytest.raises(HTTPException) as invalid:
        asyncio.run(preview_scene_object("torch", {"scene": {}, "scale": 0}))
    assert invalid.value.status_code == 422
