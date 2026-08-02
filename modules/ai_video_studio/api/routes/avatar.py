"""Avatar endpoints — virtual actor library and avatar card generation."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from modules.ai_video_studio.core.exceptions import AIError

router = APIRouter()


class AvatarGenerateRequest(BaseModel):
    avatar_id: str = Field(..., min_length=1)
    width: int = Field(default=640, ge=64, le=2048)
    height: int = Field(default=640, ge=64, le=2048)


class AvatarGenerateResponse(BaseModel):
    avatar_id: str
    file_path: str
    width: int
    height: int


@router.get("", summary="List available avatars")
async def list_avatars(style: str | None = None):
    """List the virtual actor library, optionally filtered by style."""
    from modules.ai_video_studio.services.avatar_engine import AvatarEngine

    engine = AvatarEngine()
    avatars = engine.list_avatars()
    if style:
        avatars = [a for a in avatars if a["style"] == style]
    return {"success": True, "data": {"avatars": avatars}}


@router.post("/generate", response_model=AvatarGenerateResponse, status_code=201)
async def generate_avatar_card(req: AvatarGenerateRequest):
    """Generate a styled avatar card image for a virtual actor.

    Returns the path to the generated PNG (placeholder presenter card,
    ready to be overlaid by the render pipeline).
    """
    from modules.ai_video_studio.services.avatar_engine import AvatarEngine, AVATAR_LIBRARY

    avatar = next((a for a in AVATAR_LIBRARY if a.id == req.avatar_id), None)
    if avatar is None:
        raise HTTPException(status_code=404, detail=f"Avatar '{req.avatar_id}' not found")

    engine = AvatarEngine()
    try:
        path = await engine.generate_avatar_card(
            avatar, width=req.width, height=req.height
        )
    except AIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict()) from e
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Avatar card generation failed: {e}") from e

    return AvatarGenerateResponse(
        avatar_id=avatar.id, file_path=path, width=req.width, height=req.height
    )
