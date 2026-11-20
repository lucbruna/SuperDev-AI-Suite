"""Project CRUD endpoints."""
from __future__ import annotations
import math
import uuid
from modules.ai_video_studio.core.local_store import PersistentDict
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    resolution: str = "1920x1080"
    aspect_ratio: str = "16:9"
    frame_rate: int = 30
    video_codec: str = "libx264"
    audio_codec: str = "aac"
    container: str = "mp4"
    ai_prompt: str | None = None
    ai_style: str | None = None
    ai_language: str = "en"
    tags: dict | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    resolution: str | None = None
    aspect_ratio: str | None = None
    frame_rate: int | None = None
    video_codec: str | None = None
    audio_codec: str | None = None
    container: str | None = None
    status: str | None = None
    ai_prompt: str | None = None
    ai_style: str | None = None
    ai_language: str | None = None
    tags: dict | None = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    status: str
    resolution: str
    aspect_ratio: str
    frame_rate: int
    duration_seconds: float
    video_codec: str
    audio_codec: str
    container: str
    ai_prompt: str | None = None
    ai_style: str | None = None
    ai_language: str
    tags: dict | None = None
    thumbnail_url: str | None = None
    output_url: str | None = None
    scene_count: int = 0



_projects = PersistentDict("projects")
# Remove only the fixed IDs used by the old bundled demo fixtures. Real user
# records use generated UUIDs and are left untouched.
for _demo_id in ["p1","p2","p3","p4"]:
    if _demo_id in _projects:
        del _projects[_demo_id]


def _video_job_project_summary(record: dict, existing: dict | None = None) -> dict:
    """Build the project-catalog summary for one real video-generation job."""
    params = record.get("params") if isinstance(record.get("params"), dict) else {}
    project_id = str(record.get("project_id") or "").strip()
    if not project_id:
        raise ValueError("A video job must have a project_id")

    resolution = str(record.get("resolution") or params.get("resolution") or "1280x720")
    try:
        width, height = (int(part) for part in resolution.lower().split("x", 1))
        if width <= 0 or height <= 0:
            raise ValueError("resolution dimensions must be positive")
        divisor = math.gcd(width, height)
        aspect_ratio = f"{width // divisor}:{height // divisor}"
    except (TypeError, ValueError, ZeroDivisionError):
        aspect_ratio = "16:9"

    current = dict(existing or {})
    current.update({
        "id": project_id,
        "name": current.get("name") or "Workspace de vídeos",
        "description": current.get("description") or "Projeto local vinculado aos vídeos gerados.",
        "status": ("completed" if record.get("status") == "completed" else "failed" if record.get("status") == "failed" else "active"),
        "resolution": resolution,
        "aspect_ratio": current.get("aspect_ratio") or aspect_ratio,
        "frame_rate": int(record.get("frame_rate") or params.get("frame_rate") or current.get("frame_rate") or 24),
        "duration_seconds": float(record.get("video_duration") or params.get("duration_seconds") or current.get("duration_seconds") or 0),
        "video_codec": current.get("video_codec") or "libx264",
        "audio_codec": current.get("audio_codec") or "aac",
        "container": current.get("container") or "mp4",
        "ai_prompt": params.get("prompt") or current.get("ai_prompt"),
        "ai_style": params.get("style") or current.get("ai_style"),
        "ai_language": params.get("voice_language") or current.get("ai_language") or "pt-BR",
        "tags": current.get("tags"),
        "thumbnail_url": current.get("thumbnail_url"),
        "output_url": record.get("output_url") or current.get("output_url"),
        "scene_count": len(record.get("_source_scenes") or []) or int(params.get("num_scenes") or current.get("scene_count") or 0),
    })
    return current


def sync_video_job_project(record: dict) -> None:
    """Ensure the local project catalog reflects the latest real video job."""
    project_id = str(record.get("project_id") or "").strip()
    if not project_id:
        return
    _projects[project_id] = _video_job_project_summary(record, _projects.get(project_id))


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(data: ProjectCreate):
    pid = str(uuid.uuid4())
    project = {"id": pid, **data.model_dump(), "status": "draft", "duration_seconds": 0.0, "thumbnail_url": None, "output_url": None, "scene_count": 0}
    _projects[pid] = project
    return ProjectResponse(**project)


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(status: str | None = Query(None), limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    items = list(_projects.values())
    if status:
        items = [p for p in items if p["status"] == status]
    return [ProjectResponse(**p) for p in items[offset:offset + limit]]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    return ProjectResponse(**_projects[project_id])


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, data: ProjectUpdate):
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    _projects[project_id].update(data.model_dump(exclude_unset=True))
    return ProjectResponse(**_projects[project_id])


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: str):
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    del _projects[project_id]
