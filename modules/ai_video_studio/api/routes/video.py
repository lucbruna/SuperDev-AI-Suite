"""Video generation endpoints — triggers AI pipelines."""
from __future__ import annotations
import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

router = APIRouter()


class VideoGenerateRequest(BaseModel):
    project_id: str = Field(..., description="Project to generate video for")
    prompt: str = Field(..., min_length=1, max_length=5000)
    style: str = Field(default="cinematic")
    duration_seconds: float = Field(default=10.0, ge=1.0, le=300.0)
    resolution: str = Field(default="1920x1080")
    aspect_ratio: str = Field(default="16:9")
    frame_rate: int = Field(default=30, ge=1, le=120)
    num_scenes: int = Field(default=3, ge=1, le=20)
    voice_over: bool = Field(default=True)
    voice_language: str = Field(default="en")
    music_genre: str | None = Field(default=None)


class VideoGenerateResponse(BaseModel):
    job_id: str
    project_id: str
    status: str
    estimated_seconds: float
    message: str


class VideoStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float
    current_step: str | None = None
    output_url: str | None = None
    error: str | None = None


_jobs: dict[str, dict] = {}


@router.post("/generate", response_model=VideoGenerateResponse, status_code=202)
async def generate_video(req: VideoGenerateRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "job_id": job_id, "project_id": req.project_id, "status": "queued",
        "progress": 0.0, "current_step": "Queued", "output_url": None, "error": None,
    }

    async def _run(job_id: str, r: VideoGenerateRequest):
        _jobs[job_id].update(status="processing", current_step="Planning scenes", progress=0.1)
        try:
            from modules.ai_video_studio.pipelines.text_to_video import TextToVideoPipeline
            pipeline = TextToVideoPipeline()
            result = await pipeline.execute(
                prompt=r.prompt, duration=r.duration_seconds,
                resolution=r.resolution, num_scenes=r.num_scenes, style=r.style,
            )
            _jobs[job_id].update(status="completed", progress=1.0, output_url=result.get("output_url"), current_step="Done")
        except Exception as e:
            _jobs[job_id].update(status="failed", error=str(e))

    background_tasks.add_task(_run, job_id, req)
    return VideoGenerateResponse(job_id=job_id, project_id=req.project_id, status="queued", estimated_seconds=req.duration_seconds * 2, message="Video generation queued")


@router.get("/jobs/{job_id}", response_model=VideoStatusResponse)
async def get_video_job_status(job_id: str):
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return VideoStatusResponse(**_jobs[job_id])


@router.get("/jobs", response_model=list[VideoStatusResponse])
async def list_video_jobs(project_id: str | None = None):
    jobs = list(_jobs.values())
    if project_id:
        jobs = [j for j in jobs if j["project_id"] == project_id]
    return [VideoStatusResponse(**j) for j in jobs]
