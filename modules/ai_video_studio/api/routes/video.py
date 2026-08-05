"""Video generation endpoints — real MP4 generation.

Uses the Volume 3 ``TextToVideoEngine`` (Ollama scene planning → PIL frame
rendering → FFmpeg encoding → optional AI voice narration) instead of the
old placeholder pipeline. Jobs run in the background and expose real
``output_url`` values that can be downloaded from ``/downloads/...``.
"""
from __future__ import annotations

import asyncio
import uuid
from math import gcd

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field, field_validator

from modules.ai_video_studio.api.urls import to_download_url

router = APIRouter()


# Aspect ratios accepted for video generation (reduced via gcd). Anything else
# is rejected with HTTP 422 — no silent fallback to 720p.
#
# Note: keys must be fully reduced forms. ``21:9`` reduces to ``7:3``, and real
# ultrawide resolutions reduce to 64:27 (2560x1080, 5120x2160) or 43:18
# (3440x1440), so those are what we list.
_STANDARD_ASPECT_RATIOS: dict[tuple[int, int], str] = {
    (16, 9): "16:9 landscape",
    (9, 16): "9:16 vertical (Shorts/Reels/TikTok)",
    (1, 1): "1:1 square",
    (4, 3): "4:3",
    (64, 27): "21:9 ultrawide",
    (43, 18): "21:9 ultrawide",
}

_MIN_DIMENSION = 64
_MAX_DIMENSION = 7680  # 8K UHD longest edge


class VideoGenerateRequest(BaseModel):
    project_id: str = Field(..., description="Project to generate video for")
    prompt: str = Field(..., min_length=1, max_length=5000)
    style: str = Field(default="cinematic")
    duration_seconds: float = Field(default=6.0, ge=1.0, le=600.0, description="Video length in seconds (up to 10 minutes)")
    resolution: str = Field(default="1280x720")
    frame_rate: int = Field(default=24, ge=1, le=120)
    num_scenes: int = Field(default=3, ge=1, le=20)
    voiceover: bool = Field(default=False, description="Add AI narration (edge-tts/gTTS/pyttsx3)")
    voice_id: str = Field(default="default")
    voice_language: str = Field(default="en")
    voice_speed: float = Field(default=1.0, ge=0.5, le=2.0)
    voice_pitch: float = Field(default=1.0, ge=0.5, le=2.0)
    voiceover_mode: str = Field(default="per_scene", pattern="^(per_scene|single)$", description="per_scene = one clip per scene, single = one flat track")
    llm_timeout: float = Field(default=60.0, ge=1.0, le=300.0)
    # Platform format preset selected in the dashboard (shorts/reels/tiktok/
    # youtube/square) or "custom" when the user tweaked a dimension manually.
    format: str = Field(default="custom", max_length=32)

    @field_validator("resolution")
    @classmethod
    def _validate_resolution(cls, v: str) -> str:
        _parse_resolution(v)
        return v


class VideoGenerateResponse(BaseModel):
    job_id: str
    project_id: str
    status: str
    estimated_seconds: float
    message: str
    format: str | None = None


class VoiceoverClip(BaseModel):
    """One narrated scene placed on the video timeline."""

    index: int
    text: str = ""
    start: float = 0.0  # cumulative offset of the scene in the video (seconds)
    end: float = 0.0
    audio_path: str | None = None
    tts_engine: str | None = None
    audio_duration: float | None = None
    error: str | None = None


class VoiceoverInfo(BaseModel):
    """Voiceover result metadata — per-scene clips and their timeline offsets.

    ``reason`` explains an overall failure (e.g. TTS down); ``clips[i].error``
    captures a per-scene synthesis failure while the rest keep playing.
    """

    muxed: bool = False
    output_path: str | None = None
    bytes: int | None = None
    narration_style: str = "single_track"  # per_scene | single_track
    narration: str | None = None
    clips: list[VoiceoverClip] = []
    total_duration: float | None = None
    voice_id: str | None = None
    language: str | None = None
    tts_engine: str | None = None
    audio_duration: float | None = None
    # Per-scene audio track report (from export_audio_track). Preserved for
    # backward compatibility with clients that read voiceover.audio.
    audio: dict | None = None
    reason: str | None = None


class VideoStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float
    current_step: str | None = None
    output_url: str | None = None
    output_path: str | None = None
    file_size_bytes: int | None = None
    ai_planner: str | None = None
    # Real duration of the generated MP4, probed with ffprobe after encoding.
    video_duration: float | None = None
    resolution: str | None = None
    frame_rate: int | None = None
    # Live render progress — frames encoded so far / total frame budget.
    frames_rendered: int | None = None
    total_frames: int | None = None
    # Platform format preset chosen at generation time (shorts/reels/tiktok/
    # youtube/square) and a snapshot of every generation param, persisted so
    # the dashboard list can label jobs ("Shorts 9:16") and re-run them.
    format: str | None = None
    params: dict | None = None
    voiceover: VoiceoverInfo | None = None
    error: str | None = None


_jobs: dict[str, dict] = {}


@router.post("/generate", response_model=VideoGenerateResponse, status_code=202)
async def generate_video(req: VideoGenerateRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "job_id": job_id, "project_id": req.project_id, "status": "queued",
        "progress": 0.0, "current_step": "Queued", "output_url": None,
        "output_path": None, "file_size_bytes": None, "ai_planner": None,
        "video_duration": None, "resolution": req.resolution,
        "frame_rate": req.frame_rate, "frames_rendered": None,
        "total_frames": None, "format": req.format,
        # Full param snapshot (every request field, including the prompt) so
        # the list can label the job and re-run it with identical settings.
        "params": req.model_dump(exclude={"project_id"}),
        "voiceover": None, "error": None,
    }

    async def _run(job_id: str, r: VideoGenerateRequest) -> None:
        record = _jobs[job_id]
        record.update(status="processing", current_step="Planning scenes", progress=0.1)
        try:
            from modules.ai_video_studio.ai_video_generator.text_to_video.text_to_video_engine import TextToVideoEngine

            width, height = _parse_resolution(r.resolution)

            # Live render progress → job record (read by the polling endpoint).
            # Rendering maps to 10%–85% of overall progress; the remaining
            # 15% covers voiceover/muxing before the job flips to 100%.
            def _on_render_progress(rendered: int, total: int) -> None:
                record["frames_rendered"] = rendered
                record["total_frames"] = total
                record["current_step"] = "Rendering frames"
                if total > 0:
                    record["progress"] = 0.1 + 0.75 * min(rendered, total) / total

            result = await TextToVideoEngine().generate_async(
                {
                    "prompt": r.prompt,
                    "params": {
                        "duration": r.duration_seconds,
                        "num_scenes": r.num_scenes,
                        "fps": r.frame_rate,
                        "width": width,
                        "height": height,
                        "voiceover": r.voiceover,
                        "voice_id": r.voice_id,
                        "voice_language": r.voice_language,
                        "voice_speed": r.voice_speed,
                        "voice_pitch": r.voice_pitch,
                        "voiceover_mode": r.voiceover_mode,
                        "llm_timeout": r.llm_timeout,
                    },
                },
                progress_callback=_on_render_progress,
            )
            output_path = result["output_path"]
            record.update(
                status="completed",
                progress=1.0,
                current_step="Done",
                output_path=output_path,
                output_url=to_download_url(output_path),
                file_size_bytes=result.get("output_bytes", 0),
                ai_planner=result.get("ai_planner"),
                video_duration=await _probe_video_duration(output_path),
                voiceover=result.get("voiceover"),
            )
        except Exception as e:  # noqa: BLE001 — surface any failure on the job
            record.update(status="failed", error=str(e))

    background_tasks.add_task(_run, job_id, req)
    return VideoGenerateResponse(
        job_id=job_id,
        project_id=req.project_id,
        status="queued",
        estimated_seconds=req.duration_seconds * 2,
        message="Video generation queued",
        format=req.format,
    )


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


async def _probe_video_duration(path: str) -> float | None:
    """Probe the real MP4 duration via ffprobe (None when ffprobe is missing)."""
    try:
        from modules.ai_video_studio.ai_dubbing.export_dubbing import probe_duration

        return await asyncio.to_thread(probe_duration, path) or None
    except Exception:  # noqa: BLE001 — probe failure is non-fatal
        return None


def _parse_resolution(resolution: str) -> tuple[int, int]:
    """Parse ``WxH`` (or ``W:H``) and validate against standard aspect ratios.

    Accepts every multiple of the standard ratios (16:9, 9:16, 1:1, 4:3,
    21:9 ultrawide) within the dimension bounds. Raises ``ValueError`` for
    unparseable
    strings, out-of-range edges, or non-standard aspect ratios — surfaced as
    HTTP 422 by the ``resolution`` field validator on the request model.
    """
    raw = resolution
    try:
        parts = resolution.lower().replace(":", "x").split("x")
        width = int(parts[0].strip())
        height = int(parts[1].strip())
    except (ValueError, IndexError):
        raise ValueError(
            f"Invalid resolution {raw!r}: expected WxH "
            "(e.g. 1280x720, 1920x1080, 1080x1920, 1080x1080)"
        ) from None

    if width < _MIN_DIMENSION or height < _MIN_DIMENSION:
        raise ValueError(
            f"Invalid resolution {width}x{height}: edges must be at least "
            f"{_MIN_DIMENSION} pixels"
        )
    if width > _MAX_DIMENSION or height > _MAX_DIMENSION:
        raise ValueError(
            f"Invalid resolution {width}x{height}: edges must be at most "
            f"{_MAX_DIMENSION} pixels"
        )

    g = gcd(width, height)
    ratio = (width // g, height // g)
    if ratio not in _STANDARD_ASPECT_RATIOS:
        supported = ", ".join(sorted(set(_STANDARD_ASPECT_RATIOS.values())))
        raise ValueError(
            f"Invalid resolution {width}x{height}: aspect ratio {ratio[0]}:{ratio[1]} "
            f"is not supported. Supported ratios: {supported}"
        )
    return width, height
