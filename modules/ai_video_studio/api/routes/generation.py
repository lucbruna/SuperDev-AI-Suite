"""Real generation endpoints — Volume 3 engines over HTTP.

Exposes the real media-producing engines (image, image-to-video,
video-to-video, animation, physics, asset) and serves the generated files
from ``modules/downloads/``.

All blocking engine calls run via :func:`asyncio.to_thread` so the event
loop is never blocked by FFmpeg/PIL work.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from modules.ai_video_studio.api.urls import to_download_url
from modules.ai_video_studio.core.exceptions import VideoStudioError
from modules.ai_video_studio.media.output_paths import DOWNLOADS_DIR

router = APIRouter()


# ── Request/response models ───────────────────────────────────────
class ImageGenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    style: str = Field(default="realistic")
    width: int = Field(default=1024, ge=64, le=4096)
    height: int = Field(default=1024, ge=64, le=4096)


class ImageToVideoRequest(BaseModel):
    image_ref: str = Field(..., min_length=1, description="Path to an existing image, or a descriptive ref")
    duration_seconds: float = Field(default=4.0, ge=1.0, le=60.0)
    fps: int = Field(default=24, ge=1, le=60)
    camera_motion: str = Field(default="parallax")
    width: int = Field(default=1280, ge=64, le=4096)
    height: int = Field(default=720, ge=64, le=4096)


class VideoToVideoRequest(BaseModel):
    video_ref: str = Field(default="", description="Path to an existing video, or empty to auto-generate a demo clip")
    operation: str = Field(default="style_transfer")
    style: str = Field(default="cinematic")
    target: str = Field(default="1080p")
    to_fps: int = Field(default=60, ge=1, le=240)
    strength: float = Field(default=0.4, ge=0.0, le=1.0)


class AnimationRequest(BaseModel):
    character: str = Field(default="default")
    action: str = Field(default="walk")
    duration_seconds: float = Field(default=3.0, ge=0.5, le=60.0)
    fps: int = Field(default=24, ge=1, le=60)


class PhysicsRequest(BaseModel):
    duration_seconds: float = Field(default=4.0, ge=1.0, le=60.0)
    fps: int = Field(default=24, ge=1, le=60)
    seed: int = Field(default=7)


class AssetGenerateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    kind: str = Field(default="texture", description="texture | sound | music")


# ── Endpoints ─────────────────────────────────────────────────────
@router.post("/images/generate", summary="Generate a real image (14 styles)")
async def generate_image(req: ImageGenerateRequest):
    """Generate a real PNG via the AI Image Generator."""
    from modules.ai_video_studio.ai_image_generator import get_image_engine

    try:
        record = await asyncio.to_thread(
            get_image_engine().generate, req.prompt, style=req.style, size=(req.width, req.height),
        )
    except VideoStudioError as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict()) from e
    result = record["result"]
    return {
        "success": True,
        "data": {**result, "download_url": to_download_url(result["output_path"])},
    }


@router.post("/videos/image-to-video", summary="Animate an image into a real MP4")
async def image_to_video(req: ImageToVideoRequest):
    """Animate a source image (or procedural scene) into a real MP4."""
    from modules.ai_video_studio.ai_video_generator.image_to_video.image_to_video_engine import ImageToVideoEngine

    try:
        result = await asyncio.to_thread(
            ImageToVideoEngine().generate,
            {
                "prompt": req.image_ref,
                "params": {
                    "duration": req.duration_seconds,
                    "fps": req.fps,
                    "camera_motion": req.camera_motion,
                    "width": req.width,
                    "height": req.height,
                },
            },
        )
    except VideoStudioError as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict()) from e
    return {"success": True, "data": {**result, "download_url": to_download_url(result["output_path"])}}


@router.post("/videos/video-to-video", summary="Transform a video (style/upscale/fps/denoise)")
async def video_to_video(req: VideoToVideoRequest):
    """Apply a real FFmpeg transform to an input video."""
    from modules.ai_video_studio.ai_video_generator.video_to_video.video_converter import VideoConverter

    try:
        result = await asyncio.to_thread(
            VideoConverter().convert,
            {
                "prompt": "",
                "params": {
                    "video_ref": req.video_ref,
                    "operation": req.operation,
                    "style": req.style,
                    "target": req.target,
                    "to_fps": req.to_fps,
                    "strength": req.strength,
                },
            },
        )
    except VideoStudioError as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict()) from e
    return {"success": True, "data": {**result, "download_url": to_download_url(result["output_path"])}}


@router.post("/animations/generate", summary="Render a character animation into a real MP4")
async def generate_animation(req: AnimationRequest):
    """Render a skeleton character animation (walk/run/jump/idle/wave/sit)."""
    from modules.ai_video_studio.ai_animation import get_animation_engine

    result = await asyncio.to_thread(
        get_animation_engine().animate,
        character=req.character,
        action=req.action,
        duration=req.duration_seconds,
        fps=req.fps,
    )
    return {"success": True, "data": {**result, "download_url": to_download_url(result["output_path"])}}


@router.post("/physics/simulate", summary="Render a particle physics simulation into a real MP4")
async def simulate_physics(req: PhysicsRequest):
    """Run the physics engine and render falling particles with gravity."""
    from modules.ai_video_studio.ai_physics import get_physics_engine

    result = await asyncio.to_thread(
        get_physics_engine().render_simulation,
        duration=req.duration_seconds,
        fps=req.fps,
        seed=req.seed,
    )
    return {"success": True, "data": {**result, "download_url": to_download_url(result["output_path"])}}


@router.post("/assets/generate", summary="Generate a real placeholder asset (PNG/WAV)")
async def generate_asset(req: AssetGenerateRequest):
    """Generate a texture PNG or sound WAV into the asset library."""
    from modules.ai_video_studio.asset_library import AssetManager

    result = await asyncio.to_thread(
        AssetManager().generate_placeholder, name=req.name, kind=req.kind,
    )
    return {"success": True, "data": {**result, "download_url": to_download_url(result["output_path"])}}


# ── File serving ──────────────────────────────────────────────────
@router.get("/downloads/{kind}/{filename}", summary="Download a generated media file")
async def download_media(kind: str, filename: str):
    """Serve a generated file from ``modules/downloads/<kind>/<filename>``.

    Path traversal is blocked via ``Path(...).name``: only the final path
    component is used, and it must exist inside the downloads tree.
    """
    safe_kind = Path(kind).name
    safe_file = Path(filename).name
    path = DOWNLOADS_DIR / safe_kind / safe_file
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {kind}/{filename}")
    return FileResponse(str(path))
