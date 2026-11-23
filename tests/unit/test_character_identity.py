"""Tests for DARKSTUDIO character identity contracts."""
from __future__ import annotations

import pytest

from modules.ai_video_studio.media.character_identity import (
    apply_character_identities,
    audit_character_identity,
    build_character_identity_prompt,
    create_character_identity,
)


def _profile(**overrides):
    values = {
        "character_id": "mia",
        "name": "Mia",
        "visual_identity": "Girl with brown tied-up hair and a red dress.",
        "reference_asset_ids": ["asset-mia-front"],
        "invariants": ["same face and proportions", "same red dress"],
        "forbidden_variations": ["do not change hair color", "do not change outfit"],
    }
    values.update(overrides)
    return create_character_identity(**values)


def test_create_character_identity_deduplicates_references_and_rules():
    profile = _profile(
        reference_asset_ids=["asset-mia-front", "asset-mia-front", "asset-mia-side"],
        invariants=["same face", "same face"],
    )
    assert profile["reference_asset_ids"] == ["asset-mia-front", "asset-mia-side"]
    assert profile["invariants"] == ["same face"]
    assert profile["review_status"] == "reference_assets_attached"


@pytest.mark.parametrize("character_id", ["", "../mia", "mia/leo", "x" * 65])
def test_create_character_identity_rejects_unsafe_ids(character_id):
    with pytest.raises(ValueError):
        _profile(character_id=character_id)


def test_create_character_identity_requires_visual_identity():
    with pytest.raises(ValueError, match="visual_identity is required"):
        _profile(visual_identity=" ")


def test_prompt_uses_reference_assets_and_never_claims_verification():
    prompt = build_character_identity_prompt(_profile())
    assert "asset-mia-front" in prompt["prompt"]
    assert "PRESERVE:" in prompt["prompt"]
    assert prompt["requires_human_review"] is False
    assert prompt["pixel_identity_verified"] is False


def test_prompt_without_reference_requires_human_review():
    prompt = build_character_identity_prompt(_profile(reference_asset_ids=[]))
    assert prompt["requires_human_review"] is True
    assert "No approved visual reference" in prompt["prompt"]


def test_apply_character_identities_only_uses_explicit_scene_assignments():
    profiles = {"mia": _profile()}
    scene = {"description": "A room", "character_ids": ["mia"]}
    result = apply_character_identities(scene, profiles)
    assert len(result["character_identity_prompts"]) == 1
    assert result["character_identity_review"]["status"] == "references_attached"
    assert "character_identity_prompts" not in scene


def test_apply_character_identities_reports_unknown_profiles():
    result = apply_character_identities({"character_ids": ["leo"]}, {"mia": _profile()})
    assert result["character_identity_review"]["status"] == "unknown_character"
    assert result["character_identity_review"]["unknown_character_ids"] == ["leo"]


def test_audit_character_identity_reports_review_without_pixel_claims():
    profiles = {"mia": _profile(), "leo": _profile(character_id="leo", name="Leo")}
    report = audit_character_identity(
        [{"_source_scene_index": 4, "character_ids": ["mia"]},
         {"character_ids": ["leo", "missing"]},
         {"description": "No character assigned"}],
        profiles,
    )
    assert report["scene_count"] == 3
    assert report["ready_scene_count"] == 1
    assert report["review_scene_count"] == 1
    assert report["pixel_identity_verified"] is False
    assert report["scenes"][1]["unknown_character_ids"] == ["missing"]
    assert report["scenes"][2]["status"] == "no_characters_assigned"


def test_scene_character_ids_must_be_a_list():
    with pytest.raises(ValueError, match="must be a list"):
        apply_character_identities({"character_ids": "mia"}, {"mia": _profile()})
