"""DARKSTUDIO endpoints for discovering and previewing studio profiles."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from modules.ai_video_studio.media.studio_profiles import (
    PROFILES,
    apply_studio_profile,
    get_studio_profile,
)
from modules.ai_video_studio.media.characters import (
    PRESETS as CHARACTER_PRESETS,
    VALID_EXPRESSIONS,
    VALID_POSES,
    add_character,
)
from modules.ai_video_studio.media.scene_library import (
    compose_scene_object,
    list_scene_objects,
)

router = APIRouter()


def _profile_payload(studio_id: str) -> dict[str, Any]:
    profile = get_studio_profile(studio_id)
    return {
        "id": profile.studio_id,
        "name": profile.display_name,
        "visual_language": profile.visual_language,
        "background": {
            "type": profile.background_type,
            "colors": list(profile.background_colors),
        },
        "palette": list(profile.palette),
        "noise": profile.noise,
        "grading_strength": profile.grading_strength,
        "text": {
            "default_color": profile.default_text_color,
            "default_size": profile.default_text_size,
        },
        "camera_defaults": dict(profile.camera_defaults),
    }


@router.get("", tags=["DARKSTUDIO"])
async def list_studios() -> dict[str, Any]:
    """List the two registered studios and their visual contracts."""
    studios = [_profile_payload(studio_id) for studio_id in sorted(PROFILES)]
    return {"count": len(studios), "studios": studios}


@router.get("/{studio_id}", tags=["DARKSTUDIO"])
async def get_studio(studio_id: str) -> dict[str, Any]:
    """Return one studio's immutable visual configuration."""
    try:
        return _profile_payload(studio_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{studio_id}/scene-preview", tags=["DARKSTUDIO"])
async def preview_scene_profile(
    studio_id: str,
    scene: dict[str, Any],
) -> dict[str, Any]:
    """Apply a studio profile to scene data without rendering or mutating it."""
    try:
        prepared = apply_studio_profile(studio_id, scene)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"studio_id": studio_id, "scene": prepared}


@router.get("/library/characters", tags=["DARKSTUDIO"])
async def list_studio_characters(studio_id: str | None = None) -> dict[str, Any]:
    """List stable procedural character identities and their visual contracts."""
    catalog = {
        "leo": {
            "id": "leo", "name": "Leo", "studio_id": "whymentary",
            "appearance": {
                "hair": "blonde",
                "outfit": "blue shirt and dark trousers",
                "hair_color": CHARACTER_PRESETS["leo"].hair,
                "clothing_color": CHARACTER_PRESETS["leo"].clothing,
                "trousers_color": CHARACTER_PRESETS["leo"].trousers,
            },
            "supported_poses": sorted(VALID_POSES),
            "supported_expressions": sorted(VALID_EXPRESSIONS),
        },
        "mia": {
            "id": "mia", "name": "Mia", "studio_id": "whymentary",
            "appearance": {
                "hair": "brown hair tied up", "outfit": "red dress",
                "hair_color": CHARACTER_PRESETS["mia"].hair,
                "clothing_color": CHARACTER_PRESETS["mia"].clothing,
                "hair_tied": True,
            },
            "supported_poses": sorted(VALID_POSES),
            "supported_expressions": sorted(VALID_EXPRESSIONS),
        },
        "historical_narrator": {
            "id": "historical_narrator", "name": "Narrador histórico",
            "studio_id": "historical_documentary",
            "appearance": {
                "hair_color": CHARACTER_PRESETS["historical_narrator"].hair,
                "clothing_color": CHARACTER_PRESETS["historical_narrator"].clothing,
            },
            "supported_poses": sorted(VALID_POSES),
            "supported_expressions": sorted(VALID_EXPRESSIONS),
        },
    }
    if studio_id is not None and studio_id not in PROFILES:
        raise HTTPException(status_code=404, detail=f"Unknown studio '{studio_id}'")
    items = [
        item for item in catalog.values()
        if studio_id is None or item["studio_id"] == studio_id
    ]
    return {"count": len(items), "characters": items}


@router.get("/library/characters/{character_id}", tags=["DARKSTUDIO"])
async def get_studio_character(character_id: str) -> dict[str, Any]:
    """Return one reusable character identity."""
    result = await list_studio_characters()
    character = next(
        (item for item in result["characters"] if item["id"] == character_id), None
    )
    if character is None:
        raise HTTPException(status_code=404, detail=f"Unknown character '{character_id}'")
    return character


@router.post("/library/characters/{character_id}/scene-preview", tags=["DARKSTUDIO"])
async def preview_studio_character(
    character_id: str, payload: dict[str, Any]
) -> dict[str, Any]:
    """Compose a character into editable scene primitives."""
    await get_studio_character(character_id)
    try:
        scene = add_character(
            payload.get("scene") or {},
            character_id,
            x=float(payload.get("x", 160)),
            y=float(payload.get("y", 300)),
            scale=float(payload.get("scale", 1.0)),
            pose=str(payload.get("pose", "neutral")),
            expression=str(payload.get("expression", "neutral")),
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"character_id": character_id, "scene": scene}



@router.get("/library/objects", tags=["DARKSTUDIO"])
async def list_studio_objects(studio_id: str | None = None) -> dict[str, Any]:
    """List reusable props and environment objects for a studio."""
    try:
        objects = list_scene_objects(studio_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"count": len(objects), "objects": objects}


@router.post("/library/objects/{object_id}/scene-preview", tags=["DARKSTUDIO"])
async def preview_scene_object(
    object_id: str, payload: dict[str, Any]
) -> dict[str, Any]:
    """Compose one library object into editable SceneCanvas primitives."""
    try:
        scene = compose_scene_object(
            payload.get("scene") or {},
            object_id,
            x=float(payload.get("x", 0)),
            y=float(payload.get("y", 0)),
            scale=float(payload.get("scale", 1.0)),
            motion_start_frame=int(payload.get("motion_start_frame", 0)),
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"object_id": object_id, "scene": scene}
