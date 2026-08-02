"""Skill endpoints — install/update/uninstall/run skills and inspect the system."""
from __future__ import annotations
from typing import Any

from fastapi import APIRouter, HTTPException

from modules.ai_video_studio.skills.skill_engine import SkillNotFoundError
from modules.ai_video_studio.skills.skill_installer import SkillInstallError
from modules.ai_video_studio.skills.skill_manager import get_skill_manager
from modules.ai_video_studio.skills.skill_marketplace import get_skill_marketplace
from modules.ai_video_studio.skills.skill_scheduler import get_skill_scheduler
from modules.ai_video_studio.skills.skill_uninstaller import SkillUninstallError
from modules.ai_video_studio.skills.skill_updater import SkillUpdateError
from modules.ai_video_studio.skills.skill_validator import SkillValidationError

router = APIRouter()


@router.get("", tags=["Skills"])
async def list_skills(category: str | None = None) -> dict[str, Any]:
    manager = get_skill_manager()
    return {
        "count": len(manager.list(category)),
        "categories": manager.categories(),
        "skills": manager.list(category),
    }


@router.get("/{skill_id}", tags=["Skills"])
async def get_skill(skill_id: str) -> dict[str, Any]:
    definition = get_skill_manager().get(skill_id)
    if definition is None:
        raise HTTPException(status_code=404, detail=f"skill '{skill_id}' not found")
    from modules.ai_video_studio.skills.skill_registry import SkillRegistry

    return SkillRegistry.to_dict(definition)


@router.post("/install", tags=["Skills"])
async def install_skill(payload: dict[str, Any]) -> dict[str, Any]:
    """Install a skill from its metadata dict (id/name/version/...)."""
    from modules.ai_video_studio.skills.skill_loader import from_dict

    try:
        definition = from_dict(payload)
    except (SkillValidationError, KeyError) as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    try:
        return get_skill_manager().install(definition)
    except SkillInstallError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@router.post("/{skill_id}/update", tags=["Skills"])
async def update_skill(skill_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    from modules.ai_video_studio.skills.skill_loader import from_dict

    payload = {**payload, "id": payload.get("id", skill_id)}
    try:
        definition = from_dict(payload)
    except (SkillValidationError, KeyError) as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    try:
        return get_skill_manager().update(definition)
    except SkillUpdateError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@router.delete("/{skill_id}", tags=["Skills"])
async def uninstall_skill(skill_id: str) -> dict[str, Any]:
    try:
        return get_skill_manager().uninstall(skill_id)
    except SkillUninstallError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/{skill_id}/run", tags=["Skills"])
async def run_skill(skill_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    body = payload or {}
    context = body.get("context") or {}
    kwargs = {k: v for k, v in body.items() if k != "context"}
    try:
        result = await get_skill_manager().run(skill_id, context=context, **kwargs)
    except SkillNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return result.to_dict()


@router.get("/marketplace/list", tags=["Skills"])
async def marketplace_list(category: str | None = None) -> list[dict[str, Any]]:
    return get_skill_marketplace().list(category)


@router.get("/scheduler/snapshot", tags=["Skills"])
async def scheduler_snapshot() -> dict[str, Any]:
    return get_skill_scheduler().snapshot()
