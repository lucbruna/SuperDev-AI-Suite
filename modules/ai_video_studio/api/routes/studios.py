"""DARKSTUDIO endpoints for discovering and previewing studio profiles."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from modules.ai_video_studio.media.studio_profiles import (
    PROFILES,
    apply_studio_profile,
    get_studio_profile,
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
