"""Video generation endpoints — real MP4 generation.

Uses the Volume 3 ``TextToVideoEngine`` (Ollama scene planning → PIL frame
rendering → FFmpeg encoding → optional AI voice narration) instead of the
old placeholder pipeline. Jobs run in the background and expose real
``output_url`` values that can be downloaded from ``/downloads/...``.
"""
from __future__ import annotations

import asyncio
import uuid
from pathlib import Path
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
    generate_subtitles: bool = Field(default=False, description="Generate a timed SRT sidecar from scene narration")
    voice_id: str = Field(default="default")
    voice_language: str = Field(default="pt-BR")
    voice_speed: float = Field(default=1.0, ge=0.5, le=2.0)
    voice_pitch: float = Field(default=1.0, ge=0.5, le=2.0)
    voiceover_mode: str = Field(default="per_scene", pattern="^(per_scene|single)$", description="per_scene = one clip per scene, single = one flat track")
    llm_timeout: float = Field(default=60.0, ge=1.0, le=300.0)
    # Platform format preset selected in the dashboard (shorts/reels/tiktok/
    # youtube/square) or "custom" when the user tweaked a dimension manually.
    format: str = Field(default="custom", max_length=32)
    studio_id: str = Field(default="whymentary", pattern="^(whymentary|historical_documentary)$")
    character_ids: list[str] = Field(default_factory=list, max_length=2, description="Stable character IDs to include in every scene")
    object_ids: list[str] = Field(default_factory=list, max_length=6, description="Reusable scene object IDs to include in every scene")

    @field_validator("resolution")
    @classmethod
    def _validate_resolution(cls, v: str) -> str:
        _parse_resolution(v)
        return v

    @field_validator("character_ids")
    @classmethod
    def _validate_character_ids(cls, values: list[str]) -> list[str]:
        if len(values) != len(set(values)):
            raise ValueError("character_ids must not contain duplicates")
        return values

    @field_validator("object_ids")
    @classmethod
    def _validate_object_ids(cls, values: list[str]) -> list[str]:
        if len(values) != len(set(values)):
            raise ValueError("object_ids must not contain duplicates")
        return values


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
    subtitles: dict | None = None
    edit_timeline: dict | None = None
    edit_draft_status: str | None = None
    audio_draft_status: str | None = None
    edit_render_status: str | None = None
    edited_output_url: str | None = None
    edited_video_duration: float | None = None
    edit_render_audio: str | None = None
    edit_render_subtitles: str | None = None
    edited_subtitles: dict | None = None
    error: str | None = None



class SceneEdit(BaseModel):
    scene_index: int = Field(..., ge=0)
    duration_frames: int | None = Field(default=None, ge=1)
    transition_type: str | None = Field(default=None, pattern="^(cut|crossfade|fade_through_black)$")
    transition_duration_frames: int | None = Field(default=None, ge=2)


class TimelineEditRequest(BaseModel):
    scene_order: list[int] | None = None
    scene_edits: list[SceneEdit] = Field(default_factory=list)


class AudioTimelineClip(BaseModel):
    asset: str = Field(..., min_length=1, max_length=2048)
    start: float = Field(default=0, ge=0, le=36000)
    end: float = Field(..., gt=0, le=36000)
    trim_start: float = Field(default=0, ge=0, le=36000)
    volume: float = Field(default=1, ge=0, le=2)
    fade_in: float = Field(default=0, ge=0, le=36000)
    fade_out: float = Field(default=0, ge=0, le=36000)


class AudioTimelineEditRequest(BaseModel):
    music_clips: list[AudioTimelineClip] = Field(default_factory=list, max_length=30)
    sfx_clips: list[AudioTimelineClip] = Field(default_factory=list, max_length=100)


def _persist_job(record: dict) -> None:
    from modules.ai_video_studio.media.job_store import save_job

    save_job(record)


try:
    from modules.ai_video_studio.media.job_store import load_jobs

    _jobs: dict[str, dict] = load_jobs()
except Exception:
    # API startup remains available if the local job database needs repair.
    _jobs = {}


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
        "voiceover": None, "subtitles": None, "edit_timeline": None, "error": None,
    }

    _persist_job(_jobs[job_id])

    async def _run(job_id: str, r: VideoGenerateRequest) -> None:
        record = _jobs[job_id]
        record.update(status="processing", current_step="Planning scenes", progress=0.1)
        _persist_job(record)
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
                        "generate_subtitles": r.generate_subtitles,
                        "voice_id": r.voice_id,
                        "voice_language": r.voice_language,
                        "voice_speed": r.voice_speed,
                        "voice_pitch": r.voice_pitch,
                        "voiceover_mode": r.voiceover_mode,
                        "llm_timeout": r.llm_timeout,
                        "studio_id": r.studio_id,
                        "character_ids": r.character_ids,
                        "object_ids": r.object_ids,
                    },
                },
                progress_callback=_on_render_progress,
            )
            output_path = result["output_path"]
            subtitle_info = result.get("subtitles")
            if isinstance(subtitle_info, dict) and subtitle_info.get("file_path"):
                subtitle_info = {
                    **subtitle_info,
                    "download_url": to_download_url(subtitle_info["file_path"]),
                }
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
                subtitles=subtitle_info,
                edit_timeline=result.get("edit_timeline"),
                _source_scenes=result.get("scenes"),
                _edited_scenes=result.get("scenes"),
            )
            _persist_job(record)
        except Exception as e:  # noqa: BLE001 — surface any failure on the job
            record.update(status="failed", error=str(e))
            _persist_job(record)

    background_tasks.add_task(_run, job_id, req)
    return VideoGenerateResponse(
        job_id=job_id,
        project_id=req.project_id,
        status="queued",
        estimated_seconds=req.duration_seconds * 2,
        message="Video generation queued",
        format=req.format,
    )



@router.patch("/jobs/{job_id}/timeline")
async def update_video_job_timeline(job_id: str, req: TimelineEditRequest):
    """Persist a validated edit draft to the local SQLite job store."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if record.get("status") != "completed" or not record.get("_source_scenes"):
        raise HTTPException(status_code=409, detail="Only completed jobs with a scene plan can be edited")
    from modules.ai_video_studio.media.timeline import apply_scene_edits, build_edit_timeline

    params = record.get("params") or {}
    fps = int(params.get("frame_rate") or record.get("frame_rate") or 24)
    try:
        edited = apply_scene_edits(
            record["_source_scenes"],
            scene_order=req.scene_order,
            scene_edits=[item.model_dump(exclude_none=True) for item in req.scene_edits],
            fps=fps,
        )
        width, height = _parse_resolution(params.get("resolution") or record.get("resolution") or "1280x720")
        timeline = build_edit_timeline(edited, fps=fps, width=width, height=height)
        previous = record.get("edit_timeline") or {}
        timeline["tracks"].extend(
            track for track in previous.get("tracks", []) if track.get("type") != "video"
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    record["_edited_scenes"] = edited
    record["edit_timeline"] = timeline
    record["edit_draft_status"] = "saved"
    _persist_job(record)
    return {
        "job_id": job_id,
        "edit_timeline": timeline,
        "edit_draft_status": "persisted_local_sqlite",
        "message": "Rascunho salvo no banco SQLite local. O novo MP4 ainda precisa ser renderizado.",
    }




@router.get("/jobs/{job_id}/audio-assets")
async def list_video_job_audio_assets(job_id: str):
    """Return selectable audio assets from approved generated-media folders."""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    from modules.ai_video_studio.media.audio_timeline import list_audio_assets

    return {"job_id": job_id, "assets": list_audio_assets()}


@router.patch("/jobs/{job_id}/audio")
async def update_video_job_audio(job_id: str, req: AudioTimelineEditRequest):
    """Save music/SFX placements and their independent gain/fade controls."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if record.get("status") != "completed" or not record.get("_edited_scenes"):
        raise HTTPException(status_code=409, detail="Save a valid video timeline before editing audio")

    from modules.ai_video_studio.media.audio_timeline import validate_audio_asset
    from modules.ai_video_studio.media.timeline import build_edit_timeline

    music = [clip.model_dump() for clip in req.music_clips]
    effects = [clip.model_dump() for clip in req.sfx_clips]
    try:
        for clip in music + effects:
            validate_audio_asset(clip["asset"])
        params = record.get("params") or {}
        fps = int(params.get("frame_rate") or record.get("frame_rate") or 24)
        width, height = _parse_resolution(params.get("resolution") or record.get("resolution") or "1280x720")
        timeline = build_edit_timeline(record["_edited_scenes"], fps=fps, width=width, height=height, music_clips=music, sfx_clips=effects)
        video_duration = timeline["duration_seconds"]
        for clip in music + effects:
            effective_duration = min(clip["end"], video_duration) - clip["start"]
            if effective_duration > 0 and (clip["fade_in"] > effective_duration or clip["fade_out"] > effective_duration):
                raise ValueError("audio fade duration cannot exceed the visible clip duration")
        previous = record.get("edit_timeline") or {}
        timeline["tracks"].extend(track for track in previous.get("tracks", []) if track.get("type") != "video" and track.get("role") not in {"music", "sound_effect"})
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    record["_audio_clips"] = {"music": music, "sfx": effects}
    record["edit_timeline"] = timeline
    record["audio_draft_status"] = "saved"
    _persist_job(record)
    return {"job_id": job_id, "edit_timeline": timeline, "audio_draft_status": "saved", "message": "Faixas de música e efeitos salvas. Renderize para aplicar a mixagem ao novo MP4."}

@router.post("/jobs/{job_id}/render-edits")
async def render_video_job_edits(job_id: str):
    """Render the current edited storyboard to a new MP4; audio is not re-timed yet."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if record.get("status") != "completed" or not record.get("_edited_scenes"):
        raise HTTPException(status_code=409, detail="Save a valid timeline draft before rendering")
    if record.get("_rendering_edits"):
        raise HTTPException(status_code=409, detail="An edited render is already running")

    params = record.get("params") or {}
    scenes = record["_edited_scenes"]
    try:
        width, height = _parse_resolution(params.get("resolution") or record.get("resolution") or "1280x720")
        fps = int(params.get("frame_rate") or record.get("frame_rate") or 24)
        if not 1 <= fps <= 120:
            raise ValueError("frame_rate must be between 1 and 120")
        from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
        from modules.ai_video_studio.media.render import render_multi_scene_video
        output_path = unique_filename(get_subsystem_dir("videos"), "text_to_video_edited", "mp4")
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    record["_rendering_edits"] = True
    record["edit_render_status"] = "rendering"
    _persist_job(record)
    try:
        result = await asyncio.to_thread(
            render_multi_scene_video, scenes, output_path, fps=fps, width=width, height=height,
            require_mp4=True, studio_id=params.get("studio_id") or "whymentary",
        )
        rendered_path = result["output_path"]
        audio_status = "silent"
        final_path = rendered_path
        voiceover = record.get("voiceover") or {}
        narration_clips = voiceover.get("clips") if isinstance(voiceover, dict) else None
        single_track = (
            isinstance(voiceover, dict)
            and voiceover.get("muxed")
            and voiceover.get("narration_style") == "single_track"
        )
        if single_track:
            audio_status = "single_track_not_retimed"

        from modules.ai_video_studio.media.audio import mux_audio_into_video
        from modules.ai_video_studio.media.audio_timeline import mix_audio_timeline
        from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename

        audio_inputs = []
        has_per_scene_narration = isinstance(narration_clips, list) and any(
            isinstance(clip, dict) and clip.get("audio_path") for clip in narration_clips
        )
        if has_per_scene_narration:
            from modules.ai_video_studio.media.scene_narration import (
                build_narration_tracks,
                remap_narration_clips_for_edits,
            )
            remapped_narration = remap_narration_clips_for_edits(scenes, narration_clips, fps=fps)
            audio_inputs.extend(build_narration_tracks(remapped_narration))

        configured_audio = record.get("_audio_clips") or {}
        audio_inputs.extend(configured_audio.get("music", []))
        audio_inputs.extend(configured_audio.get("sfx", []))
        if audio_inputs:
            total_duration = int(round(result["frames"])) / fps
            audio_path = unique_filename(get_subsystem_dir("mix"), "edited_audio_mix", "wav")
            mix_result = await asyncio.to_thread(
                mix_audio_timeline, audio_inputs, audio_path, total_duration=total_duration
            )
            muxed_path = unique_filename(get_subsystem_dir("videos"), "text_to_video_edited_final", "mp4")
            mux_result = await asyncio.to_thread(
                mux_audio_into_video, rendered_path, mix_result["output_path"], muxed_path
            )
            if mux_result.get("muxed"):
                final_path = mux_result["output_path"]
                audio_status = "mixed_audio_single_track_omitted" if single_track and not has_per_scene_narration else "mixed_audio"
            else:
                audio_status = "audio_mux_failed"

        # Rebuild subtitle sidecar against the edited scene order and timing.
        subtitle_status = "not_generated"
        subtitle_info = None
        try:
            from modules.ai_video_studio.media.scene_narration import compute_scene_offsets, scene_narration_text
            from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
            from modules.ai_video_studio.services.subtitle_studio import SubtitleStudioService

            subtitle_offsets = compute_scene_offsets(scenes, fps=fps)
            subtitle_scenes = [
                {
                    "text": scene_narration_text(scene),
                    "duration": max(1, int(round(float(scene.get("duration") or 3.0) * fps))) / fps,
                    "start_offset": subtitle_offsets[index],
                }
                for index, scene in enumerate(scenes)
            ]
            subtitle_path = unique_filename(
                get_subsystem_dir("subtitles"), "edited_video_subtitles", "srt"
            )
            generated_subtitles = await asyncio.to_thread(
                SubtitleStudioService().generate_srt,
                subtitle_scenes,
                output_path=str(subtitle_path),
            )
            subtitle_info = {
                "format": "srt",
                "file_path": generated_subtitles["file_path"],
                "download_url": to_download_url(generated_subtitles["file_path"]),
                "cue_count": generated_subtitles["cue_count"],
                "duration": generated_subtitles["duration"],
            }
            subtitle_status = "regenerated"
            record["edited_subtitles"] = subtitle_info
        except Exception as subtitle_exc:
            subtitle_status = "failed"
            record["edited_subtitles"] = {
                "generated": False, "reason": str(subtitle_exc)[:200]
            }

        edited_url = to_download_url(final_path)
        edited_duration = round(result["frames"] / fps, 3)
        edited_bytes = Path(final_path).stat().st_size
        record.update(
            edited_output_path=final_path,
            edited_output_url=edited_url,
            edited_file_size_bytes=edited_bytes,
            edited_video_duration=edited_duration,
            edit_render_status="completed",
            edit_render_audio=audio_status,
            edit_render_subtitles=subtitle_status,
        )
        _persist_job(record)
        return {
            "job_id": job_id,
            "status": "completed",
            "output_url": edited_url,
            "video_duration": edited_duration,
            "file_size_bytes": edited_bytes,
            "audio_status": audio_status,
            "subtitle_status": subtitle_status,
            "subtitles": subtitle_info,
            "message": "MP4 editado renderizado com as faixas configuradas mixadas." if audio_status == "mixed_audio" else "MP4 editado renderizado com música/efeitos; a narração original em faixa única foi omitida." if audio_status == "mixed_audio_single_track_omitted" else "MP4 editado renderizado; a faixa única original não foi reposicionada automaticamente." if audio_status == "single_track_not_retimed" else "MP4 editado renderizado sem faixas de áudio configuradas." if audio_status == "silent" else "MP4 visual renderizado, mas a muxagem de áudio falhou; consulte o status do áudio.",,,
        }
    except Exception as exc:
        record["edit_render_status"] = "failed"
        record["edit_render_error"] = str(exc)[:500]
        _persist_job(record)
        raise HTTPException(status_code=500, detail="Edited video render failed") from exc
    finally:
        record["_rendering_edits"] = False

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
