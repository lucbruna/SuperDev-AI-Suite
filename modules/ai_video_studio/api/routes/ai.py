"""AI Studio endpoints — real AI generation (director/screenwriter/storyboard).

These endpoints call the platform LLM stack through
``services.ai_studio.AIStudioService``. When no provider is configured the
service falls back to a deterministic planner, so endpoints remain usable
offline (``ai_generated: false`` in the response).
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from modules.ai_video_studio.core.exceptions import AIError
from modules.ai_video_studio.database.database import get_db
from modules.ai_video_studio.services.ai_studio import (
    AIStoryboard,
    AIScreenwriter,
    AIStudioService,
)

router = APIRouter()


class GenerateProjectRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=5000)
    num_scenes: int = Field(default=3, ge=1, le=20)
    duration_seconds: float = Field(default=10.0, ge=1.0, le=600.0, description="Project duration in seconds (up to 10 minutes)")
    style: str = Field(default="cinematic")
    language: str = Field(default="en", min_length=2, max_length=10)
    provider: str | None = Field(default=None)
    model: str | None = Field(default=None)


class ExpandSceneRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=5000)
    scene: dict[str, Any] = Field(..., description="Scene to deepen")
    style: str = Field(default="cinematic")
    language: str = Field(default="en", min_length=2, max_length=10)
    provider: str | None = Field(default=None)
    model: str | None = Field(default=None)


class ScriptRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=5000)
    scenes: list[dict[str, Any]] = Field(..., min_length=1, max_length=50)
    language: str = Field(default="en", min_length=2, max_length=10)
    provider: str | None = Field(default=None)
    model: str | None = Field(default=None)


class StoryboardRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=5000)
    scenes: list[dict[str, Any]] = Field(..., min_length=1, max_length=50)
    style: str = Field(default="cinematic")
    provider: str | None = Field(default=None)
    model: str | None = Field(default=None)


@router.post("/generate-project", summary="Full AI project generation")
async def generate_project(
    req: GenerateProjectRequest,
    db: AsyncSession = Depends(get_db),
):
    """Run director → screenwriter → storyboard over a text brief.

    Returns the generated scenes (name, type, duration, script, voiceover,
    visual prompt, colors, transitions) plus provider/model metadata. When no
    LLM provider is configured this returns the deterministic fallback plan.
    """
    service = AIStudioService()
    try:
        result = await service.generate_project(
            req.prompt,
            num_scenes=req.num_scenes,
            duration=req.duration_seconds,
            style=req.style,
            language=req.language,
            provider=req.provider,
            model=req.model,
            db=db,
        )
    except AIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict()) from e
    return {"success": True, "data": result}


@router.post("/script", summary="Write scripts/voiceover for scenes")
async def write_script(req: ScriptRequest, db: AsyncSession = Depends(get_db)):
    """Screenwriter pass over existing scenes (adds script + voiceover_text)."""
    screenwriter = AIScreenwriter()
    try:
        scenes = await screenwriter.write(
            req.prompt, req.scenes, language=req.language,
            provider=req.provider, model=req.model, db=db,
        )
    except AIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict()) from e
    return {"success": True, "data": {"ai_generated": True, "scenes": scenes}}


@router.post("/storyboard", summary="Generate visual prompts for scenes")
async def generate_storyboard(req: StoryboardRequest, db: AsyncSession = Depends(get_db)):
    """Storyboard pass over existing scenes (adds visual_prompt + background_color)."""
    storyboard = AIStoryboard()
    try:
        scenes = await storyboard.generate(
            req.prompt, req.scenes, style=req.style,
            provider=req.provider, model=req.model, db=db,
        )
    except AIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict()) from e
    return {"success": True, "data": {"ai_generated": True, "scenes": scenes}}


@router.post("/expand-scene", summary="Deepen a single scene")
async def expand_scene(req: ExpandSceneRequest, db: AsyncSession = Depends(get_db)):
    """Deepen one scene: richer script, voiceover and visual prompt."""
    service = AIStudioService()
    try:
        result = await service.expand_scene(
            req.prompt, req.scene, style=req.style, language=req.language,
            provider=req.provider, model=req.model, db=db,
        )
    except AIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict()) from e
    return {"success": True, "data": result}
