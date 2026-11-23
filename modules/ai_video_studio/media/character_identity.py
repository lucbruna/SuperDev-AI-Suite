"""Reusable character identity contracts for DARKSTUDIO AI.

This module manages authored identity metadata and scene-level prompt constraints.
It does not inspect pixels or guarantee model-level identity consistency; reference
assets and human approval remain required for visual verification.
"""
from __future__ import annotations

import re
from copy import deepcopy
from typing import Any


_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,63}$")
_MAX_TEXT = 4000
_MAX_REFERENCES = 24


def _clean_text(value: Any, field: str, *, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise ValueError(f"{field} is required")
    if len(text) > _MAX_TEXT:
        raise ValueError(f"{field} must be at most {_MAX_TEXT} characters")
    return text


def create_character_identity(
    character_id: str,
    *,
    name: str,
    visual_identity: str,
    reference_asset_ids: list[str] | None = None,
    invariants: list[str] | None = None,
    forbidden_variations: list[str] | None = None,
) -> dict[str, Any]:
    """Build a validated, serializable identity profile without file-path inputs."""
    identifier = str(character_id or "").strip()
    if not _ID_RE.fullmatch(identifier):
        raise ValueError("character_id must be 1-64 safe identifier characters")
    refs = list(dict.fromkeys(str(item).strip() for item in (reference_asset_ids or []) if str(item).strip()))
    if len(refs) > _MAX_REFERENCES:
        raise ValueError(f"reference_asset_ids cannot exceed {_MAX_REFERENCES} items")
    if any(len(item) > 128 for item in refs):
        raise ValueError("reference asset IDs must be at most 128 characters")
    stable = [_clean_text(item, "invariants", required=True) for item in (invariants or [])]
    forbidden = [_clean_text(item, "forbidden_variations", required=True) for item in (forbidden_variations or [])]
    return {
        "character_id": identifier,
        "name": _clean_text(name, "name", required=True),
        "visual_identity": _clean_text(visual_identity, "visual_identity", required=True),
        "reference_asset_ids": refs,
        "invariants": list(dict.fromkeys(stable)),
        "forbidden_variations": list(dict.fromkeys(forbidden)),
        "identity_version": 1,
        "review_status": "needs_reference_review" if not refs else "reference_assets_attached",
    }


def build_character_identity_prompt(profile: dict[str, Any]) -> dict[str, Any]:
    """Return prompt constraints for a generation provider; never claims pixel validation."""
    identity = create_character_identity(
        str(profile.get("character_id") or ""),
        name=profile.get("name"),
        visual_identity=profile.get("visual_identity"),
        reference_asset_ids=profile.get("reference_asset_ids") or [],
        invariants=profile.get("invariants") or [],
        forbidden_variations=profile.get("forbidden_variations") or [],
    )
    lines = [
        f"CHARACTER IDENTITY — {identity['name']} ({identity['character_id']})",
        identity["visual_identity"],
    ]
    if identity["invariants"]:
        lines.append("PRESERVE: " + "; ".join(identity["invariants"]))
    if identity["forbidden_variations"]:
        lines.append("DO NOT CHANGE: " + "; ".join(identity["forbidden_variations"]))
    if identity["reference_asset_ids"]:
        lines.append(
            "Use the approved character reference assets: "
            + ", ".join(identity["reference_asset_ids"])
        )
    else:
        lines.append("No approved visual reference asset is attached; human review is required.")
    return {
        "character_id": identity["character_id"],
        "prompt": "\n".join(lines),
        "reference_asset_ids": identity["reference_asset_ids"],
        "requires_human_review": not bool(identity["reference_asset_ids"]),
        "pixel_identity_verified": False,
    }


def apply_character_identities(
    scene: dict[str, Any],
    profiles: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Return a copied scene with identity prompts for explicitly assigned characters."""
    result = deepcopy(scene)
    requested = result.get("character_ids") or []
    if not isinstance(requested, list):
        raise ValueError("scene.character_ids must be a list")
    prompts: list[dict[str, Any]] = []
    unknown: list[str] = []
    for raw_id in requested:
        character_id = str(raw_id).strip()
        if not character_id:
            continue
        profile = profiles.get(character_id)
        if not isinstance(profile, dict):
            unknown.append(character_id)
            continue
        prompts.append(build_character_identity_prompt(profile))
    result["character_identity_prompts"] = prompts
    result["character_identity_review"] = {
        "status": "unknown_character" if unknown else (
            "no_characters_assigned" if not prompts else (
                "needs_human_review" if any(item["requires_human_review"] for item in prompts)
                else "references_attached"
            )
        ),
        "unknown_character_ids": unknown,
        "pixel_identity_verified": False,
        "requires_human_review": bool(unknown) or any(
            item["requires_human_review"] for item in prompts
        ),
    }
    return result


def audit_character_identity(
    scenes: list[dict[str, Any]],
    profiles: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Summarize identity readiness for scenes without inferring visual similarity."""
    results = []
    for index, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            raise ValueError(f"scene {index} must be an object")
        applied = apply_character_identities(scene, profiles)
        review = applied["character_identity_review"]
        results.append({
            "scene_index": int(scene.get("_source_scene_index", index)),
            "character_ids": list(scene.get("character_ids") or []),
            "status": review["status"],
            "unknown_character_ids": review["unknown_character_ids"],
            "requires_human_review": review["requires_human_review"],
        })
    return {
        "scene_count": len(results),
        "profile_count": len(profiles),
        "ready_scene_count": sum(item["status"] == "references_attached" for item in results),
        "review_scene_count": sum(item["requires_human_review"] for item in results),
        "pixel_identity_verified": False,
        "scenes": results,
    }
