"""Render job endpoints — create, monitor, cancel render tasks."""
from __future__ import annotations
import uuid
from datetime import datetime, UTC
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class RenderCreate(BaseModel):
    project_id: str
    output_format: str = "mp4"
    output_resolution: str = "1920x1080"
    video_codec: str = "libx264"
    audio_codec: str = "aac"
    bitrate: str | None = None
    crf: int = 23
    preset: str = "medium"
    use_gpu: bool = False
    priority: int = 1


class RenderResponse(BaseModel):
    id: str
    project_id: str
    status: str
    priority: int
    progress: float
    current_step: str | None = None
    output_format: str
    output_resolution: str
    video_codec: str
    audio_codec: str
    crf: int
    preset: str
    use_gpu: bool
    output_path: str | None = None
    output_url: str | None = None
    error_message: str | None = None
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None


class RenderProgressUpdate(BaseModel):
    progress: float = Field(..., ge=0.0, le=1.0)
    current_step: str | None = None


_renders: dict[str, dict] = {}


def _seed_renders() -> dict[str, dict]:
    """Demo render jobs mirroring the frontend render center (in-memory)."""
    now = datetime.now(UTC).isoformat()
    rows: list[dict] = [
        {
            "id": "r1", "project_id": "p1", "status": "rendering", "priority": 1,
            "progress": 0.64, "current_step": "Encoding",
            "output_format": "mp4", "output_resolution": "3840x2160",
            "video_codec": "libx264", "audio_codec": "aac", "crf": 23, "preset": "medium",
            "use_gpu": True, "output_path": None, "output_url": None,
            "error_message": None, "created_at": now, "started_at": now, "completed_at": None,
        },
        {
            "id": "r2", "project_id": "p2", "status": "completed", "priority": 1,
            "progress": 1.0, "current_step": "Done",
            "output_format": "mp4", "output_resolution": "1920x1080",
            "video_codec": "libx264", "audio_codec": "aac", "crf": 23, "preset": "medium",
            "use_gpu": True, "output_path": "storage/video_studio/renders/r2.mp4",
            "output_url": "/api/v1/video-studio/downloads/videos/brand_story.mp4",
            "error_message": None, "created_at": now, "started_at": now, "completed_at": now,
        },
        {
            "id": "r3", "project_id": "p3", "status": "queued", "priority": 2,
            "progress": 0.0, "current_step": "Queued",
            "output_format": "mp4", "output_resolution": "1920x1080",
            "video_codec": "libx264", "audio_codec": "aac", "crf": 23, "preset": "medium",
            "use_gpu": False, "output_path": None, "output_url": None,
            "error_message": None, "created_at": now, "started_at": None, "completed_at": None,
        },
    ]
    return {r["id"]: r for r in rows}


_renders = _seed_renders()


@router.post("/", response_model=RenderResponse, status_code=201)
async def create_render(data: RenderCreate):
    rid = str(uuid.uuid4())
    now = datetime.now(UTC).isoformat()
    render = {
        "id": rid, "project_id": data.project_id, "status": "queued",
        "priority": data.priority, "progress": 0.0, "current_step": "Queued",
        "output_format": data.output_format, "output_resolution": data.output_resolution,
        "video_codec": data.video_codec, "audio_codec": data.audio_codec,
        "bitrate": data.bitrate, "crf": data.crf, "preset": data.preset,
        "use_gpu": data.use_gpu, "output_path": None, "output_url": None,
        "error_message": None, "created_at": now, "started_at": None, "completed_at": None,
    }
    _renders[rid] = render
    return RenderResponse(**render)


@router.get("/", response_model=list[RenderResponse])
async def list_renders(project_id: str | None = None, status: str | None = None):
    items = list(_renders.values())
    if project_id:
        items = [r for r in items if r["project_id"] == project_id]
    if status:
        items = [r for r in items if r["status"] == status]
    return [RenderResponse(**r) for r in items]


@router.get("/{render_id}", response_model=RenderResponse)
async def get_render(render_id: str):
    if render_id not in _renders:
        raise HTTPException(status_code=404, detail=f"Render {render_id} not found")
    return RenderResponse(**_renders[render_id])


@router.post("/{render_id}/start")
async def start_render(render_id: str):
    if render_id not in _renders:
        raise HTTPException(status_code=404, detail=f"Render {render_id} not found")
    r = _renders[render_id]
    if r["status"] not in ("queued", "failed"):
        raise HTTPException(status_code=400, detail=f"Cannot start render in status {r['status']}")
    r["status"] = "rendering"
    r["started_at"] = datetime.now(UTC).isoformat()
    r["current_step"] = "Encoding started"
    return {"message": "Render started", "id": render_id}


@router.post("/{render_id}/cancel")
async def cancel_render(render_id: str):
    if render_id not in _renders:
        raise HTTPException(status_code=404, detail=f"Render {render_id} not found")
    r = _renders[render_id]
    if r["status"] in ("completed", "cancelled"):
        raise HTTPException(status_code=400, detail=f"Cannot cancel render in status {r['status']}")
    r["status"] = "cancelled"
    r["completed_at"] = datetime.now(UTC).isoformat()
    return {"message": "Render cancelled", "id": render_id}


@router.patch("/{render_id}/progress", response_model=RenderResponse)
async def update_render_progress(render_id: str, data: RenderProgressUpdate):
    if render_id not in _renders:
        raise HTTPException(status_code=404, detail=f"Render {render_id} not found")
    r = _renders[render_id]
    r["progress"] = data.progress
    r["current_step"] = data.current_step
    if data.progress >= 1.0:
        r["status"] = "completed"
        r["completed_at"] = datetime.now(UTC).isoformat()
    return RenderResponse(**r)


@router.delete("/{render_id}", status_code=204)
async def delete_render(render_id: str):
    if render_id not in _renders:
        raise HTTPException(status_code=404, detail=f"Render {render_id} not found")
    del _renders[render_id]
