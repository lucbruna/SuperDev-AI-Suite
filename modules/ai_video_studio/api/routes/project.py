"""Project CRUD endpoints."""
from __future__ import annotations
import uuid
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


_projects: dict[str, dict] = {}


def _seed_projects() -> dict[str, dict]:
    """Demo workspace projects mirroring the frontend dashboard (in-memory)."""
    rows: list[dict] = [
        {
            "id": "p1", "name": "Product Launch 2026",
            "description": "Cinematic launch film for the Q1 reveal.",
            "status": "active", "resolution": "3840x2160", "aspect_ratio": "16:9",
            "frame_rate": 30, "duration_seconds": 42.0,
            "video_codec": "libx264", "audio_codec": "aac", "container": "mp4",
            "ai_prompt": "launch film with kinetic typography",
            "ai_style": "cinematic", "ai_language": "en",
            "tags": {"brand": "launch"}, "thumbnail_url": None, "output_url": None,
            "scene_count": 4,
        },
        {
            "id": "p2", "name": "Brand Story — Agriculture",
            "description": "Field-to-table brand narrative.",
            "status": "published", "resolution": "1920x1080", "aspect_ratio": "16:9",
            "frame_rate": 60, "duration_seconds": 96.0,
            "video_codec": "libx264", "audio_codec": "aac", "container": "mp4",
            "ai_prompt": None, "ai_style": "documentary", "ai_language": "pt",
            "tags": None, "thumbnail_url": None,
            "output_url": "/api/v1/video-studio/downloads/videos/brand_story.mp4",
            "scene_count": 6,
        },
        {
            "id": "p3", "name": "Finance Explainer Series",
            "description": "Quarterly results explainer.",
            "status": "rendering", "resolution": "1920x1080", "aspect_ratio": "16:9",
            "frame_rate": 30, "duration_seconds": 120.0,
            "video_codec": "libx264", "audio_codec": "aac", "container": "mp4",
            "ai_prompt": None, "ai_style": "corporate", "ai_language": "en",
            "tags": None, "thumbnail_url": None, "output_url": None,
            "scene_count": 5,
        },
        {
            "id": "p4", "name": "Ecommerce Ads Q3",
            "description": "High-converting product ad set.",
            "status": "draft", "resolution": "1080x1920", "aspect_ratio": "9:16",
            "frame_rate": 30, "duration_seconds": 15.0,
            "video_codec": "libx264", "audio_codec": "aac", "container": "mp4",
            "ai_prompt": None, "ai_style": "advertising", "ai_language": "en",
            "tags": None, "thumbnail_url": None, "output_url": None,
            "scene_count": 1,
        },
    ]
    return {r["id"]: r for r in rows}


_projects = _seed_projects()


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
