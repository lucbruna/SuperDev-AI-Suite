"""Avatar Engine API — Volume 6 AI Avatar & Digital Human Engine endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile
from modules.ai_video_studio.core.exceptions import AIError, ValidationError

router = APIRouter()


class ProfileCreate(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    style: str = "realistic"
    dimension: str = "3d"
    gender: str = "neutral"
    age_group: str = "adult"
    voice: str = "default"
    default_outfit: str = "business"
    skin_tone: str = "#c68642"
    hair_color: str = "#2b2b2b"
    hair_style: str = "medium"
    eye_color: str = "#3a2a1a"
    build: str = "average"
    height_cm: int = 172
    description: str = ""
    tags: list[str] = Field(default_factory=list)


class GenerateRequest(BaseModel):
    profile_id: str = Field(..., min_length=1)
    quality: str = "high"
    fps: int = 24
    resolution: str = "1280x720"
    seed: int | None = None


class MotionCaptureRequest(BaseModel):
    keyframes: list[dict[str, list[float] | tuple[float, float]]] = Field(..., min_length=1)
    fps: int = 24
    smooth: float = 0.5
    retarget: bool = False


class SpeakingRequest(BaseModel):
    profile_id: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)
    voice_id: str | None = None
    language: str = "en"
    emotion: str | None = None
    speed: float = Field(default=1.0, gt=0.5, le=2.0)
    pitch: float = Field(default=1.0, gt=0.5, le=2.0)
    fps: int = Field(default=24, ge=4, le=60)
    width: int = Field(default=640, ge=160, le=1920)
    height: int = Field(default=480, ge=160, le=1080)
    quality: str = "high"
    seed: int | None = None
    audio_path: str | None = Field(
        default=None, description="Optional pre-synthesized narration audio (skips TTS)"
    )


@router.get("/profiles", summary="List avatar profiles (Volume 6)")
async def list_profiles(style: str | None = None, dimension: str | None = None,
                        gender: str | None = None):
    """List all virtual actors from the domain libraries."""
    from modules.ai_video_studio.ai_avatar_engine.library import get_avatar_library

    filters = {k: v for k, v in {"style": style, "dimension": dimension, "gender": gender}.items() if v is not None}
    profiles = get_avatar_library().list(**filters)
    return {"success": True, "data": {"count": len(profiles),
                                      "profiles": [p.to_dict() for p in profiles]}}


@router.post("/profiles", summary="Register an avatar profile", status_code=201)
async def register_profile(req: ProfileCreate):
    from modules.ai_video_studio.ai_avatar_engine import get_avatar_engine

    try:
        profile = AvatarProfile.from_dict(req.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    added = get_avatar_engine().register_profile(profile)
    return {"success": True, "data": {"added": added, "profile": profile.to_dict()}}


@router.post("/generate", summary="Generate a digital human (Volume 6)")
async def generate_avatar(req: GenerateRequest):
    """Generate a full digital-human descriptor for a profile."""
    from modules.ai_video_studio.ai_avatar_engine import get_avatar_engine
    from modules.ai_video_studio.ai_avatar_engine.library import get_avatar_library

    try:
        profile = get_avatar_library().get(req.profile_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Profile '{req.profile_id}' not found") from None
    engine = get_avatar_engine()
    try:
        result = engine.generate_avatar(profile, quality=req.quality, fps=req.fps,
                                        resolution=req.resolution, seed=req.seed)
    except (ValidationError, AIError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"success": True, "data": result}


@router.get("/emotions", summary="List emotions (Volume 6)")
async def list_emotions():
    from modules.ai_video_studio.ai_avatar_engine.emotions import get_emotion_engine

    return {"success": True, "data": {"emotions": get_emotion_engine().names()}}


@router.get("/gestures", summary="List gestures (Volume 6)")
async def list_gestures():
    from modules.ai_video_studio.ai_avatar_engine.gestures import get_gesture_engine

    engine = get_gesture_engine()
    return {"success": True, "data": {"gestures": engine.names(), "all": [g.to_dict() for g in engine.all()[:30]]}}


@router.get("/clothing", summary="List clothing occasions (Volume 6)")
async def list_clothing():
    from modules.ai_video_studio.ai_avatar_engine.clothing import get_clothing_engine

    return {"success": True, "data": {"occasions": get_clothing_engine().occasions()}}


@router.get("/hairstyles", summary="List hairstyle catalogs (Volume 6)")
async def list_hairstyles(catalog: str | None = None):
    from modules.ai_video_studio.ai_avatar_engine.hairstyles import get_hairstyle_engine

    engine = get_hairstyle_engine()
    if catalog:
        try:
            styles = engine.styles(catalog)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"Unknown catalog '{catalog}'") from None
        return {"success": True, "data": {"catalog": catalog, "styles": styles}}
    return {"success": True, "data": {"catalogs": engine.catalogs()}}


@router.post("/motion-capture", summary="Process motion capture (Volume 6)")
async def process_mocap(req: MotionCaptureRequest):
    from modules.ai_video_studio.ai_avatar_engine.motion_capture import get_mocap_engine

    try:
        result = get_mocap_engine().process(req.keyframes, fps=req.fps,
                                            smooth=req.smooth, retarget=req.retarget)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"success": True, "data": result}


@router.post("/speak", summary="Generate a narrated talking-avatar video (lip-sync)")
async def speak(req: SpeakingRequest):
    """Avatar × Voice Studio × Lip Sync: narration audio + synced mouth video."""
    from modules.ai_video_studio.ai_avatar_engine.speaking import get_speaking_engine

    try:
        result = await get_speaking_engine().generate(
            req.profile_id, req.text,
            voice_id=req.voice_id, language=req.language, emotion=req.emotion,
            speed=req.speed, pitch=req.pitch, fps=req.fps,
            width=req.width, height=req.height, quality=req.quality,
            seed=req.seed, audio_path=req.audio_path,
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except (ValidationError, AIError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001 — pipeline failures surface as 500
        raise HTTPException(status_code=500, detail=f"speaking render failed: {e}") from e
    return {"success": True, "data": result}


@router.get("/speaking/voices", summary="List TTS voices for speaking avatars")
async def speaking_voices():
    """Voices available to the Voice Studio narration chain."""
    from modules.ai_video_studio.ai_voice_studio import get_voice_engine

    voices = get_voice_engine().list_voices()
    return {"success": True, "data": {"count": len(voices), "voices": voices[:50]}}


@router.get("/stats", summary="Avatar engine statistics (Volume 6)")
async def avatar_engine_stats():
    from modules.ai_video_studio.ai_avatar_engine import get_avatar_engine

    return {"success": True, "data": get_avatar_engine().stats()}
