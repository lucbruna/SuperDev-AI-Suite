"""Avatar endpoints — virtual actor library and avatar card generation."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from modules.ai_video_studio.core.exceptions import AIError, ValidationError

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


# ---------------------------------------------------------------------------
# Volume 6 — AI Avatar & Digital Human Engine endpoints
# ---------------------------------------------------------------------------


class CharacterGenerateRequest(BaseModel):
    seed: int = Field(..., ge=0)
    style: str | None = None
    dimension: str | None = None
    gender: str | None = None
    age_group: str | None = None


class PresenterGenerateRequest(BaseModel):
    script: str = Field(..., min_length=1, max_length=4000)
    actor_id: str | None = None
    style: str | None = None
    dimension: str | None = None
    gender: str | None = None
    scene_type: str = Field(default="content")
    expression: str = Field(default="neutral")
    outfit: str | None = None
    duration: float = Field(default=5.0, ge=0.5, le=120.0)
    fps: int = Field(default=24, ge=1, le=60)
    quality: str = Field(default="high")
    seed: int | None = Field(default=None, ge=0)
    render_video: bool = True


class CaptureRequest(BaseModel):
    landmarks: dict[str, list[float]] | None = None
    keypoints: dict[str, list[float]] | None = None
    frame: list[list[list[float]]] | None = None


@router.get("/actors", summary="List virtual actors (Volume 6)")
async def list_actors(
    style: str | None = None,
    dimension: str | None = None,
    gender: str | None = None,
    scene_type: str | None = None,
):
    """List the 2D/3D virtual actor library with optional filters."""
    from modules.ai_video_studio.ai_avatar import get_avatar_engine

    filters = {
        k: v for k, v in {"style": style, "dimension": dimension, "gender": gender, "scene_type": scene_type}.items()
        if v is not None
    }
    return {"success": True, "data": {"actors": get_avatar_engine().list_actors(**filters)}}


@router.get("/expressions", summary="List emotional expressions (Volume 6)")
async def list_expressions():
    from modules.ai_video_studio.ai_avatar import get_expression_engine

    engine = get_expression_engine()
    return {"success": True, "data": {"expressions": engine.names()}}


@router.get("/gestures", summary="List automatic gestures (Volume 6)")
async def list_gestures():
    from modules.ai_video_studio.ai_avatar import get_gesture_engine

    engine = get_gesture_engine()
    return {"success": True, "data": {"gestures": engine.names()}}


@router.get("/wardrobe", summary="List wardrobe occasions (Volume 6)")
async def list_wardrobe():
    from modules.ai_video_studio.ai_avatar import get_wardrobe

    wardrobe = get_wardrobe()
    return {"success": True, "data": {"occasions": wardrobe.occasions()}}


@router.post("/characters/generate", summary="Procedurally generate a character (Volume 6)")
async def generate_character(req: CharacterGenerateRequest):
    from modules.ai_video_studio.ai_avatar import get_avatar_engine

    actor = get_avatar_engine().generate_character(
        req.seed, style=req.style, dimension=req.dimension,
        gender=req.gender, age_group=req.age_group,
    )
    return {"success": True, "data": {"actor": actor}}


@router.post("/presenter", summary="Generate a virtual presenter video (Volume 6)")
async def generate_presenter(req: PresenterGenerateRequest):
    """Generate a complete virtual-presenter video from a script.

    Orchestrates actor selection, emotion/gesture planning, body sync and
    the digital-human renderer (MP4 output).
    """
    from modules.ai_video_studio.ai_avatar import get_avatar_engine

    if req.quality not in ("draft", "high", "final"):
        raise HTTPException(status_code=400, detail=f"Unknown quality '{req.quality}'")

    engine = get_avatar_engine()
    try:
        result = engine.generate_presenter(
            req.script,
            actor_id=req.actor_id,
            style=req.style,
            dimension=req.dimension,
            gender=req.gender,
            scene_type=req.scene_type,
            expression=req.expression,
            outfit=req.outfit,
            duration=req.duration,
            fps=req.fps,
            quality=req.quality,
            seed=req.seed,
            render_video=req.render_video,
        )
    except (AIError, ValidationError, KeyError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Presenter generation failed: {e}") from e

    return {"success": True, "data": result}


@router.post("/capture", summary="Capture facial/body parameters (Volume 6)")
async def capture(req: CaptureRequest):
    """Extract facial (landmarks) or body (keypoints) animation parameters."""
    from modules.ai_video_studio.ai_avatar import get_avatar_engine

    engine = get_avatar_engine()
    result: dict = {}
    if req.landmarks:
        result["facial"] = engine.capture_facial(landmarks=req.landmarks)
    if req.keypoints:
        result["body"] = engine.capture_body(keypoints=req.keypoints)
    if not result:
        raise HTTPException(status_code=400, detail="Provide landmarks or keypoints")
    return {"success": True, "data": result}
