"""Video generation endpoints — real MP4 generation.

Uses the Volume 3 ``TextToVideoEngine`` (Ollama scene planning → PIL frame
rendering → FFmpeg encoding → optional AI voice narration) instead of the
old placeholder pipeline. Jobs run in the background and expose real
``output_url`` values that can be downloaded from ``/downloads/...``.
"""
from __future__ import annotations

import asyncio
import json
import os
import subprocess
import shutil
import time
import uuid
from io import BytesIO
from pathlib import Path
from math import gcd
from typing import Any

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
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
    num_scenes: int = Field(default=3, ge=1, le=60, description="Up to 60 scenes; VidGrid mode uses 10 seconds per scene")
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
    studio_id: str = Field(default="custom", pattern="^(whymentary|historical_documentary|felt_clay|custom)$")
    character_ids: list[str] = Field(default_factory=list, max_length=20, description="Optional user-defined character references")
    object_ids: list[str] = Field(default_factory=list, max_length=6, description="Optional user-defined recurring object references; at most six per generation")
    scene_image_mode: str = Field(default="auto", pattern="^(procedural|ai|auto)$", description="Procedural scenes or per-scene local diffusion image generation")
    scene_image_steps: int = Field(default=20, ge=1, le=60)
    scene_image_seed: int | None = Field(default=None, ge=0, le=2147483647, description="Optional reproducible base seed for all scene images")
    scene_image_timeout: float = Field(default=180.0, ge=1.0, le=900.0, description="Per-scene provider timeout; auto mode falls back after the first provider failure")
    vidgrid_compatible: bool = Field(default=False, description="Render every storyboard clip at exactly 10 seconds for VidGrid")

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


class SceneImageEditRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000)
    negative_prompt: str = Field(default="", max_length=2000)
    denoising_strength: float = Field(default=0.45, ge=0.05, le=0.95)
    steps: int = Field(default=20, ge=1, le=60)
    cfg_scale: float = Field(default=7.0, ge=1.0, le=20.0)
    seed: int = Field(default=-1, ge=-1, le=2147483647, description="-1 for random, otherwise a reproducible image seed")
    stage_only: bool = Field(default=False, description="Store the generated image as a candidate until explicit approval")


class SceneImageBatchItem(BaseModel):
    scene_index: int = Field(..., ge=0)
    prompt: str = Field(..., min_length=1, max_length=4000)
    negative_prompt: str = Field(default="", max_length=2000)
    seed: int = Field(default=-1, ge=-1, le=2147483647)


class SceneImageBatchEditRequest(BaseModel):
    scenes: list[SceneImageBatchItem] = Field(..., min_length=1, max_length=60)


class SceneClipRebuildRequest(BaseModel):
    scene_indices: list[int] | None = Field(
        default=None, min_length=1, max_length=60,
        description="Stable scene indices to rebuild; omit to rebuild every repairable scene",
    )

    @field_validator("scene_indices")
    @classmethod
    def _validate_scene_indices(cls, values: list[int] | None) -> list[int] | None:
        if values is not None and len(values) != len(set(values)):
            raise ValueError("scene_indices must not contain duplicates")
        return values


class SceneNarrationRegenerateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    voice_id: str | None = Field(default=None, max_length=120)
    language: str | None = Field(default=None, max_length=20)
    speed: float | None = Field(default=None, ge=0.5, le=2.0)
    pitch: float | None = Field(default=None, ge=0.5, le=2.0)
    emotion: str | None = Field(default=None, max_length=80)


class DependencyImpactRequest(BaseModel):
    changed_asset_ids: list[str] = Field(..., min_length=1, max_length=100)

    @field_validator("changed_asset_ids")
    @classmethod
    def _validate_changed_asset_ids(cls, values: list[str]) -> list[str]:
        if len(values) != len(set(values)):
            raise ValueError("changed_asset_ids must not contain duplicates")
        if any(not value.strip() or len(value) > 200 for value in values):
            raise ValueError("asset IDs must be non-empty and at most 200 characters")
        return values


class DependencyExecutionRequest(DependencyImpactRequest):
    confirmed: bool = False


class SceneMotionRequest(BaseModel):
    motion_prompt: str = Field(..., min_length=1, max_length=4000)
    negative_prompt: str = Field(default="", max_length=2000)
    provider_timeout: float = Field(default=900.0, ge=5.0, le=3600.0)


class ImageEditRequest(BaseModel):
    source_path: str = Field(..., min_length=1, max_length=2048)
    prompt: str = Field(..., min_length=1, max_length=4000)
    negative_prompt: str = Field(default="", max_length=2000)
    denoising_strength: float = Field(default=0.45, ge=0.05, le=0.95)
    steps: int = Field(default=20, ge=1, le=60)
    cfg_scale: float = Field(default=7.0, ge=1.0, le=20.0)


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
    failure_info: dict[str, Any] | None = None


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
    # Included by both GET /jobs and GET /jobs/{job_id}; the dashboard uses
    # this field to keep the job identity contract consistent after polling.
    project_id: str | None = None
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
    audio_settings: dict | None = None
    audio_analysis: dict | None = None
    av_sync_analysis: dict | None = None
    visual_intelligence: dict | None = None
    mp4_visual_analysis: dict | None = None
    image_similarity_analysis: dict | None = None
    scene_image_mode: str | None = None
    scene_assets: list[dict] | None = None
    scene_image_candidates: dict[str, list[dict]] | None = None
    storyboard_report: dict | None = None
    vidgrid_compatible: bool | None = None
    clip_duration_seconds: float | None = None
    scene_clips: list[dict] | None = None
    edit_render_ducking: dict | None = None
    edit_render_normalization: dict | None = None
    edit_render_loudness: dict | None = None
    edit_render_encoded_audio: dict | None = None
    edit_render_quality: dict | None = None
    edit_render_status: str | None = None
    edit_render_recovery: dict[str, Any] | None = None
    edit_render_transition_policy: dict | None = None
    edit_preview_url: str | None = None
    edit_preview_duration: float | None = None
    edit_preview_width: int | None = None
    edit_preview_height: int | None = None
    edit_preview_fps: int | None = None
    edited_output_url: str | None = None
    edited_video_duration: float | None = None
    edit_render_audio: str | None = None
    edit_render_subtitles: str | None = None
    edited_subtitles: dict | None = None
    output_validation: dict | None = None
    scene_progress: list[dict[str, Any]] | None = None
    failure_info: dict[str, Any] | None = None
    scene_clip_rebuild_queue: dict[str, Any] | None = None
    asset_health: dict[str, Any] | None = None
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
    pan: float = Field(default=0, ge=-1, le=1, description="Stereo balance: -1 left, 0 center, 1 right")
    fade_in: float = Field(default=0, ge=0, le=36000)
    fade_out: float = Field(default=0, ge=0, le=36000)
    loop: bool = Field(default=False, description="Repeat a short source to fill the timeline clip; use for music only")


class AudioTimelineEditRequest(BaseModel):
    music_clips: list[AudioTimelineClip] = Field(default_factory=list, max_length=30)
    sfx_clips: list[AudioTimelineClip] = Field(default_factory=list, max_length=100)
    ducking_enabled: bool = True
    ducking_db: float = Field(default=9.0, ge=0, le=24)
    ducking_threshold_db: float = Field(default=-36.0, ge=-60, le=-12)
    ducking_attack: float = Field(default=0.08, gt=0, le=2)
    ducking_release: float = Field(default=0.35, gt=0, le=5)
    normalization_enabled: bool = True
    normalization_target_dbfs: float = Field(default=-18.0, ge=-60, le=0)
    normalization_max_gain_db: float = Field(default=6.0, ge=0, le=24)
    loudness_normalization_enabled: bool = False
    target_lufs: float = Field(default=-14.0, ge=-36, le=-5)
    true_peak_db: float = Field(default=-1.0, ge=-9, le=0)
    loudness_range: float = Field(default=11.0, ge=1, le=20)
    compressor_enabled: bool = False
    compressor_threshold_db: float = Field(default=-18.0, ge=-60, le=0)
    compressor_ratio: float = Field(default=3.0, ge=1, le=20)
    compressor_attack: float = Field(default=0.01, ge=0.001, le=2)
    compressor_release: float = Field(default=0.12, ge=0.001, le=5)
    compressor_makeup_db: float = Field(default=0.0, ge=-12, le=24)
    eq_enabled: bool = False
    eq_low_db: float = Field(default=0.0, ge=-12, le=12)
    eq_mid_db: float = Field(default=0.0, ge=-12, le=12)
    eq_high_db: float = Field(default=0.0, ge=-12, le=12)
    mastering_preset: str = Field(default="custom", pattern="^(custom|voice|documentary|music|cinematic_sfx)$")


def _persist_job(record: dict) -> None:
    from modules.ai_video_studio.media.job_store import save_job

    save_job(record)
    # Keep the project dashboard aligned with the durable SQLite job record.
    # A catalog write failure must not abort a video render; the next checkpoint
    # retries the summary synchronization.
    try:
        from modules.ai_video_studio.api.routes.project import sync_video_job_project

        sync_video_job_project(record)
        record.pop("project_sync_warning", None)
    except Exception as exc:  # noqa: BLE001
        record["project_sync_warning"] = str(exc)[:240]
    try:
        from modules.ai_video_studio.api.routes.scene import sync_video_job_scenes

        sync_video_job_scenes(record)
        record.pop("scene_sync_warning", None)
    except Exception as exc:  # noqa: BLE001
        record["scene_sync_warning"] = str(exc)[:240]
    try:
        from modules.ai_video_studio.api.routes.assets import sync_video_job_assets

        sync_video_job_assets(record)
        record.pop("asset_sync_warning", None)
    except Exception as exc:  # noqa: BLE001
        record["asset_sync_warning"] = str(exc)[:240]

def _merge_scene_checkpoint(record: dict[str, Any], event: dict[str, Any]) -> None:
    """Merge one durable scene snapshot and its completed assets into a job."""
    try:
        scene_index = int(event.get("scene_index", -1))
    except (TypeError, ValueError):
        return
    if scene_index < 0:
        return

    snapshot = event.get("scene_snapshot")
    if isinstance(snapshot, dict):
        scenes = [dict(item) for item in (record.get("_source_scenes") or []) if isinstance(item, dict)]
        while len(scenes) <= scene_index:
            scenes.append({})
        scenes[scene_index] = {**scenes[scene_index], **snapshot, "_source_scene_index": scene_index}
        record["_source_scenes"] = scenes
        edited = [dict(item) for item in (record.get("_edited_scenes") or []) if isinstance(item, dict)]
        while len(edited) <= scene_index:
            edited.append({})
        edited[scene_index] = {**edited[scene_index], **snapshot, "_source_scene_index": scene_index}
        record["_edited_scenes"] = edited

    image_path = event.get("image_path")
    if image_path:
        assets = record.setdefault("scene_assets", [])
        asset = next((item for item in assets if int(item.get("scene_index", -1)) == scene_index), None)
        if asset is None:
            asset = {"scene_index": scene_index}
            assets.append(asset)
        asset.update({
            "image_path": str(image_path),
            "image_url": to_download_url(str(image_path)),
            "provider": event.get("image_provider") or asset.get("provider"),
            "seed": event.get("image_seed", asset.get("seed")),
            "status": "generated",
        })

    narration_path = event.get("narration_path")
    if narration_path:
        from modules.ai_video_studio.media.output_paths import get_subsystem_dir

        voice_root = Path(get_subsystem_dir("voice")).resolve()
        safe_narration = Path(str(narration_path)).resolve()
        if voice_root in safe_narration.parents and safe_narration.is_file() and safe_narration.stat().st_size > 0:
            voiceover = record.setdefault("voiceover", {"narration_style": "per_scene", "clips": []})
            voiceover["narration_style"] = "per_scene"
            narration_clips = voiceover.setdefault("clips", [])
            saved_clip = next(
                (item for item in narration_clips if int(item.get("index", -1)) == scene_index),
                None,
            )
            if saved_clip is None:
                saved_clip = {"index": scene_index}
                narration_clips.append(saved_clip)
            saved_clip.update({
                "index": scene_index,
                "text": str(event.get("narration_text") or ""),
                "audio_path": str(safe_narration),
                "tts_engine": event.get("narration_engine"),
                "audio_duration": event.get("narration_duration"),
            })
            narration_clips.sort(key=lambda item: int(item.get("index", 0)))

    clip_path = event.get("clip_path")
    if clip_path:
        from modules.ai_video_studio.media.output_paths import get_subsystem_dir

        video_root = Path(get_subsystem_dir("videos")).resolve()
        safe_clip_path = Path(str(clip_path)).resolve()
        if (
            video_root not in safe_clip_path.parents
            or not safe_clip_path.is_file()
            or safe_clip_path.stat().st_size <= 0
        ):
            return
        clips = record.setdefault("scene_clips", [])
        clip = next((item for item in clips if int(item.get("scene_index", -1)) == scene_index), None)
        if clip is None:
            clip = {"scene_index": scene_index}
            clips.append(clip)
        clip.update({
            "output_path": str(safe_clip_path),
            "output_url": to_download_url(str(safe_clip_path)),
            "bytes": event.get("clip_bytes"),
            "duration": event.get("clip_duration", clip.get("duration")),
            "fps": event.get("clip_fps", clip.get("fps")),
            "width": event.get("clip_width", clip.get("width")),
            "height": event.get("clip_height", clip.get("height")),
            "audio_status": event.get("clip_audio_status", clip.get("audio_status")),
            "status": "ready",
        })
        # Fingerprint the exact narration source used by a successful mux so
        # future voice edits can invalidate and rebuild this scene clip.
        narration_value = event.get("clip_narration_path")
        if clip.get("audio_status") == "per_scene_narration_muxed" and narration_value:
            from modules.ai_video_studio.media.output_paths import get_subsystem_dir

            voice_root = Path(get_subsystem_dir("voice")).resolve()
            narration_path = Path(str(narration_value)).resolve()
            if voice_root in narration_path.parents and narration_path.is_file():
                try:
                    clip["source_narration_fingerprint"] = _asset_sha256(narration_path)
                except OSError:
                    clip.pop("source_narration_fingerprint", None)
        clips.sort(key=lambda item: int(item.get("scene_index", 0)))


def _asset_sha256(path: Path) -> str:
    import hashlib
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_scene_narration_asset(value: str | Path) -> Path:
    """Resolve a per-scene narration file only from the project's voice assets."""
    from modules.ai_video_studio.media.output_paths import get_subsystem_dir

    voice_root = Path(get_subsystem_dir("voice")).resolve()
    narration_path = Path(value).resolve()
    if voice_root not in narration_path.parents or not narration_path.is_file():
        raise ValueError("Scene narration is missing or outside the approved voice asset directory")
    if narration_path.stat().st_size <= 0:
        raise ValueError("Scene narration asset is empty")
    return narration_path


def _ordered_vidgrid_clip_paths(record: dict, scenes: list[dict]) -> list[str]:
    """Return a complete, ordered set of safe, non-empty VidGrid clip files."""
    from modules.ai_video_studio.media.output_paths import get_subsystem_dir

    video_root = Path(get_subsystem_dir("videos")).resolve()
    clips_by_index = {
        _safe_record_index(item.get("scene_index")): item
        for item in (record.get("scene_clips") or [])
        if isinstance(item, dict)
        and (not item.get("status") or item.get("status") in {"updated", "completed", "ready"})
        and item.get("output_path")
    }
    ordered_indices = [
        _safe_record_index(scene.get("_source_scene_index", index), index)
        for index, scene in enumerate(scenes)
    ]
    paths: list[str] = []
    invalid: list[int] = []
    voiceover = record.get("voiceover")
    voiceover = voiceover if isinstance(voiceover, dict) else {}
    narration_by_scene = {
        _safe_record_index(item.get("index")): item
        for item in (voiceover.get("clips") or [])
        if isinstance(item, dict)
    }
    voice_root = Path(get_subsystem_dir("voice")).resolve()
    for scene_index in ordered_indices:
        clip = clips_by_index.get(scene_index)
        value = clip.get("output_path") if clip else None
        path = Path(str(value)).resolve() if value else None
        if path is None or video_root not in path.parents or not path.is_file() or path.stat().st_size <= 0:
            invalid.append(scene_index)
            continue
        # VidGrid accepts ten-second scene files. Refuse known mismatches
        # rather than silently exporting a mixed-duration clip set.
        try:
            clip_duration = float(clip.get("duration")) if clip.get("duration") is not None else None
        except (TypeError, ValueError):
            clip_duration = -1.0
        if clip_duration is not None and abs(clip_duration - 10.0) > 0.05:
            invalid.append(scene_index)
            continue
        # Metadata can be stale or forged: inspect the actual MP4 container
        # whenever FFprobe is installed, and enforce its measured duration.
        probe = _probe_media_asset(path, "scene_clip")
        if probe.get("status") in {"corrupt", "unreadable"}:
            invalid.append(scene_index)
            continue
        measured_duration = probe.get("duration_seconds")
        if measured_duration is not None and abs(float(measured_duration) - 10.0) > 0.05:
            invalid.append(scene_index)
            continue
        # A scene clip must not pass final export when its required per-scene
        # narration failed to mux. The final timeline also mixes narration,
        # but accepting a silent source clip here hides a broken clip artifact
        # and makes standalone VidGrid downloads incorrect.
        if voiceover.get("narration_style") == "per_scene":
            narration = narration_by_scene.get(scene_index) or {}
            narration_value = narration.get("audio_path")
            # A scene with dialogue requires a real, muxed audio stream in its
            # standalone clip. Missing source audio or unverifiable MP4 audio
            # must not be presented as a ready VidGrid asset.
            scene = next(
                (item for position, item in enumerate(scenes)
                 if _safe_record_index(item.get("_source_scene_index", position), position) == scene_index),
                {},
            )
            requires_narration = bool(
                str(scene.get("voiceover_text") or scene.get("narration") or "").strip()
            )
            if requires_narration and not narration_value:
                invalid.append(scene_index)
                continue
            if narration_value:
                narration_path = Path(str(narration_value)).resolve()
                if (voice_root not in narration_path.parents
                        or not narration_path.is_file()
                        or narration_path.stat().st_size <= 0):
                    invalid.append(scene_index)
                    continue
                if clip.get("audio_status") != "per_scene_narration_muxed":
                    invalid.append(scene_index)
                    continue
                if probe.get("probe_status") != "passed" or probe.get("audio_stream_count", 0) < 1:
                    invalid.append(scene_index)
                    continue
                saved_fingerprint = clip.get("source_narration_fingerprint")
                if saved_fingerprint and saved_fingerprint != _asset_sha256(narration_path):
                    invalid.append(scene_index)
                    continue
            saved_fingerprint = clip.get("source_narration_fingerprint")
            if saved_fingerprint and saved_fingerprint != _asset_sha256(narration_path):
                invalid.append(scene_index)
                continue
        elif voiceover.get("narration_style") == "single_track" and (
            voiceover.get("output_path") or voiceover.get("muxed")
        ):
            # A single master track cannot be assumed to align with separately
            # downloaded/reordered 10-second clips. Require per-scene TTS for
            # a VidGrid package whose individual clips must carry their audio.
            invalid.append(scene_index)
            continue
        paths.append(str(path))
    if invalid:
        raise HTTPException(
            status_code=409,
            detail=f"VidGrid clips are missing, empty or outside the approved video directory for scenes {invalid}. Rebuild stale clips before final export.",
        )
    return paths


def _scene_clip_recovery_plan(record: dict) -> dict:
    """Compare saved VidGrid clips with active scene images and render profile."""
    from modules.ai_video_studio.media.output_paths import get_subsystem_dir
    scenes = record.get("_edited_scenes") or record.get("_source_scenes") or []
    clips = {_safe_record_index(item.get("scene_index")): item for item in (record.get("scene_clips") or []) if isinstance(item, dict)}
    image_root = Path(get_subsystem_dir("images")).resolve()
    video_root = Path(get_subsystem_dir("videos")).resolve()
    voice_root = Path(get_subsystem_dir("voice")).resolve()
    voiceover = record.get("voiceover")
    voiceover = voiceover if isinstance(voiceover, dict) else {}
    narration_by_scene = {
        _safe_record_index(item.get("index")): item
        for item in (voiceover.get("clips") or [])
        if isinstance(item, dict)
    }
    params = record.get("params") or {}
    try:
        width, height = _parse_resolution(record.get("resolution") or params.get("resolution") or "1280x720")
        fps = int(record.get("frame_rate") or params.get("frame_rate") or 24)
    except (TypeError, ValueError):
        width, height, fps = 0, 0, 0
    items: list[dict[str, Any]] = []
    repair: list[int] = []
    for position, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            continue
        scene_index = _safe_record_index(scene.get("_source_scene_index", position), position)
        clip = clips.get(scene_index)
        reasons: list[str] = []
        warnings: list[str] = []
        image_value = scene.get("background_image_path")
        image_path = Path(str(image_value)).resolve() if image_value else None
        image_fingerprint = None
        asset_record = next(
            (item for item in (record.get("scene_assets") or [])
             if isinstance(item, dict) and _safe_record_index(item.get("scene_index")) == scene_index),
            {},
        )
        image_mode = str(params.get("scene_image_mode") or record.get("scene_image_mode") or "auto")
        procedural_source = (
            image_mode == "procedural"
            or asset_record.get("status") == "fallback"
            or asset_record.get("provider") == "procedural_fallback"
        )
        image_ready = False
        if image_path is not None and image_root in image_path.parents and image_path.is_file():
            try:
                image_fingerprint = _asset_sha256(image_path)
                image_ready = True
            except OSError:
                reasons.append("approved_image_unreadable")
        elif procedural_source:
            image_ready = True
            warnings.append("procedural_scene_without_image_asset")
        else:
            reasons.append("approved_image_missing_or_unsafe")
        if clip is None:
            reasons.append("clip_missing")
        else:
            if clip.get("status") == "stale":
                reasons.append("clip_marked_stale")
            clip_value = clip.get("output_path")
            clip_path = Path(str(clip_value)).resolve() if clip_value else None
            if clip_path is None or video_root not in clip_path.parents or not clip_path.is_file() or clip_path.stat().st_size <= 0:
                reasons.append("clip_file_missing_or_unsafe")
            if clip.get("width") not in (None, width) or clip.get("height") not in (None, height):
                reasons.append("resolution_changed")
            if clip.get("fps") not in (None, fps):
                reasons.append("frame_rate_changed")
            if clip.get("duration") is not None:
                try:
                    if abs(float(clip.get("duration")) - 10.0) > 0.05:
                        reasons.append("vidgrid_clip_duration_not_10_seconds")
                except (TypeError, ValueError):
                    reasons.append("vidgrid_clip_duration_invalid")
            else:
                warnings.append("legacy_clip_without_duration_metadata")
            if clip_path is not None and clip_path.is_file() and video_root in clip_path.parents:
                probe = _probe_media_asset(clip_path, "scene_clip")
                if probe.get("status") in {"corrupt", "unreadable"}:
                    reasons.append("vidgrid_clip_mp4_invalid")
                measured_duration = probe.get("duration_seconds")
                if measured_duration is not None and abs(float(measured_duration) - 10.0) > 0.05:
                    reasons.append("vidgrid_clip_measured_duration_not_10_seconds")
                elif probe.get("probe_status") == "not_verified":
                    warnings.append("vidgrid_clip_mp4_not_verified")
            saved_fingerprint = clip.get("source_image_fingerprint")
            if saved_fingerprint and image_fingerprint and saved_fingerprint != image_fingerprint:
                reasons.append("source_image_changed")
            elif not saved_fingerprint:
                warnings.append("legacy_clip_without_image_fingerprint")
            narration_fingerprint = None
            if voiceover.get("narration_style") == "per_scene":
                narration = narration_by_scene.get(scene_index) or {}
                narration_value = narration.get("audio_path")
                narration_path = Path(str(narration_value)).resolve() if narration_value else None
                requires_narration = bool(
                    str(scene.get("voiceover_text") or scene.get("narration") or "").strip()
                )
                if narration_path is not None and voice_root in narration_path.parents and narration_path.is_file() and narration_path.stat().st_size > 0:
                    try:
                        narration_fingerprint = _asset_sha256(narration_path)
                    except OSError:
                        reasons.append("scene_narration_unreadable")
                elif requires_narration:
                    reasons.append("scene_narration_missing_or_unsafe")
                elif narration_value:
                    warnings.append("scene_narration_missing_or_unsafe")
                saved_narration_fingerprint = clip.get("source_narration_fingerprint")
                if narration_fingerprint and clip.get("audio_status") != "per_scene_narration_muxed":
                    reasons.append("scene_narration_not_muxed")
                if narration_fingerprint and clip.get("audio_status") == "per_scene_narration_muxed":
                    if probe.get("probe_status") != "passed":
                        reasons.append("vidgrid_clip_audio_not_verified")
                    elif probe.get("audio_stream_count", 0) < 1:
                        reasons.append("vidgrid_clip_audio_stream_missing")
                if saved_narration_fingerprint and narration_fingerprint and saved_narration_fingerprint != narration_fingerprint:
                    reasons.append("source_narration_changed")
                elif narration_fingerprint and not saved_narration_fingerprint and clip.get("audio_status") == "per_scene_narration_muxed":
                    warnings.append("legacy_clip_without_narration_fingerprint")
        if reasons and image_ready:
            repair.append(scene_index)
        items.append({"scene_index": scene_index, "status": "needs_rebuild" if reasons else "ready",
                      "reasons": sorted(set(reasons)), "warnings": warnings,
                      "source_image_fingerprint": image_fingerprint,
                      "source_narration_fingerprint": narration_fingerprint if clip is not None and voiceover.get("narration_style") == "per_scene" else None,
                      "clip_exists": bool(clip and clip.get("output_path") and Path(str(clip["output_path"])).resolve().is_file())})
    return {"scene_count": len(scenes), "ready_count": sum(item["status"] == "ready" for item in items),
            "repairable_count": len(repair),
            "blocked_count": sum(item["status"] == "needs_rebuild" and any(reason in item["reasons"] for reason in ("approved_image_missing_or_unsafe", "approved_image_unreadable")) for item in items),
            "repair_scene_indices": repair, "scenes": items}


def _reconcile_scene_clip_queue_after_restart(record: dict, durable_task_active: bool) -> None:
    """Keep durable VidGrid work resumable after an API process restart."""
    queue = record.get("scene_clip_rebuild_queue")
    if not isinstance(queue, dict) or queue.get("status") not in {"queued", "processing"}:
        return
    queue["current_scene_index"] = None
    queue["updated_at"] = time.time()
    record["_scene_clip_rebuild_worker"] = False
    if durable_task_active:
        # The durable worker will reclaim queued work or an expired lease.
        queue["status"] = "queued"
        record["_scene_clip_rebuild_scheduled"] = True
        queue["recovery_note"] = (
            "Reconstrução persistida preservada. O worker retomará as cenas pendentes "
            "assim que a tarefa estiver disponível."
        )
    else:
        queue["status"] = "interrupted"
        record["_scene_clip_rebuild_scheduled"] = False
        queue["recovery_note"] = (
            "A API reiniciou sem uma tarefa durável ativa. Os resultados concluídos foram preservados; "
            "use recovery-plan para reenfileirar somente as cenas reparáveis."
        )


try:
    from modules.ai_video_studio.media.job_store import (
        load_jobs, mark_interrupted_jobs, mark_interrupted_edit_renders,
        has_active_task_for_job,
    )

    _jobs: dict[str, dict] = load_jobs()
    # Jobs cannot resume an interrupted FFmpeg/model subprocess. Mark them
    # explicitly failed instead of leaving a permanent "processing" status.
    mark_interrupted_jobs(_jobs)
    # An edit export can be interrupted even when the source generation job
    # itself is already completed. Preserve its editable assets and unlock retry.
    mark_interrupted_edit_renders(_jobs)
    for _job_record in _jobs.values():
        _queue = _job_record.get("scene_clip_rebuild_queue")
        if isinstance(_queue, dict) and _queue.get("status") in {"queued", "processing"}:
            _task_active = has_active_task_for_job(
                str(_job_record.get("job_id") or ""), "scene_clip_rebuild"
            )
            _reconcile_scene_clip_queue_after_restart(_job_record, _task_active)
            try:
                _persist_job(_job_record)
            except Exception:
                pass
        _execution = _job_record.get("dependency_rebuild_execution")
        if (isinstance(_execution, dict)
                and _execution.get("status") in {"queued", "processing"}
                and not has_active_task_for_job(str(_job_record.get("job_id") or ""), "dependency_rebuild")):
            _execution["status"] = "interrupted"
            _execution["updated_at"] = time.time()
            _execution["recovery_note"] = (
                "A API foi reiniciada antes da conclusão. A execução foi preservada como interrompida; revise o grafo e o recovery-plan antes de reenfileirar."
            )
            try:
                _persist_job(_job_record)
            except Exception:
                pass
except Exception:
    # API startup remains available if the local job database needs repair.
    _jobs = {}


_scene_batch_jobs: set[str] = set()
_scene_batch_tasks: dict[str, asyncio.Task] = {}


@router.post("/jobs/{job_id}/scenes/{scene_index}/image-upload", status_code=201)
async def upload_video_job_scene_image(
    job_id: str, scene_index: int, file: UploadFile = File(...)
):
    """Upload a user-owned image as a reviewable candidate for one scene."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if scene_index < 0:
        raise HTTPException(status_code=422, detail="scene_index must be non-negative")
    if job_id in _scene_batch_jobs or record.get("_rendering_edits") or record.get("_rebuilding_scene_clips") or record.get("_scene_clip_rebuild_scheduled"):
        raise HTTPException(status_code=409, detail="Scene assets are locked by an active operation")
    if record.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Images can only be uploaded after video generation completes")

    source_scenes = record.get("_edited_scenes") or record.get("_source_scenes") or []
    position = next(
        (i for i, item in enumerate(source_scenes)
         if isinstance(item, dict) and str(item.get("_source_scene_index", i)) == str(scene_index)),
        None,
    )
    if position is None and scene_index < len(source_scenes):
        position = scene_index
    if position is None:
        raise HTTPException(status_code=404, detail="Scene index not found")

    buckets = record.get("scene_image_candidates")
    existing = buckets.get(str(scene_index), []) if isinstance(buckets, dict) else []
    if isinstance(existing, list) and len(existing) >= 8:
        raise HTTPException(status_code=409, detail="This scene already has the maximum of eight pending image candidates")

    allowed_mime = {"image/png", "image/jpeg", "image/webp"}
    if file.content_type not in allowed_mime:
        raise HTTPException(status_code=415, detail="Upload only PNG, JPEG or WebP images")
    content = await file.read(20 * 1024 * 1024 + 1)
    if not content:
        raise HTTPException(status_code=422, detail="Uploaded image is empty")
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image exceeds the 20 MB upload limit")

    try:
        from PIL import Image
        with Image.open(BytesIO(content)) as probe:
            image_format = str(probe.format or "").upper()
            width, height = probe.size
            probe.verify()
        expected_format = {"image/png": "PNG", "image/jpeg": "JPEG", "image/webp": "WEBP"}[file.content_type]
        if image_format != expected_format:
            raise ValueError("The uploaded file content does not match its MIME type")
        if width < 64 or height < 64 or width > 7680 or height > 7680 or width * height > 40_000_000:
            raise ValueError("Image dimensions must be between 64 and 7680 pixels per side and at most 40 megapixels")
        with Image.open(BytesIO(content)) as source_image:
            normalized = source_image.convert("RGBA" if "A" in source_image.getbands() else "RGB")
            buffer = BytesIO()
            normalized.save(buffer, format="PNG", optimize=True)
            png_bytes = buffer.getvalue()
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Invalid or unreadable image: {str(exc)[:180]}") from exc

    from modules.ai_video_studio.media.output_paths import get_subsystem_dir
    image_root = Path(get_subsystem_dir("images")).resolve()
    upload_dir = (image_root / job_id / "uploads").resolve()
    if image_root not in upload_dir.parents:
        raise HTTPException(status_code=422, detail="Invalid image destination")
    upload_dir.mkdir(parents=True, exist_ok=True)
    image_path = upload_dir / f"scene_{scene_index:03d}_{uuid.uuid4().hex}.png"
    image_path.write_bytes(png_bytes)

    candidate_id = uuid.uuid4().hex
    candidate = {
        "candidate_id": candidate_id,
        "scene_index": scene_index,
        "image_path": str(image_path.resolve()),
        "image_url": to_download_url(str(image_path.resolve())),
        "provider": "user_upload",
        "operation": "manual_upload",
        "prompt": "Imagem enviada manualmente pelo usuário",
        "negative_prompt": "",
        "seed": -1,
        "status": "pending_approval",
        "original_filename": Path(file.filename or "imagem").name[:160],
        "mime_type": "image/png",
        "file_size_bytes": len(png_bytes),
    }
    from modules.ai_video_studio.media.scene_visual_asset_workflow import stage_scene_image_candidate
    try:
        updated = stage_scene_image_candidate(record, scene_index, candidate)
        _persist_job(updated)
        record.clear()
        record.update(updated)
    except (ValueError, RuntimeError) as exc:
        image_path.unlink(missing_ok=True)
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        image_path.unlink(missing_ok=True)
        raise HTTPException(status_code=503, detail="Could not persist uploaded scene image") from exc

    return {
        "job_id": job_id, "scene_index": scene_index, "candidate_id": candidate_id,
        "image_url": candidate["image_url"], "provider": "user_upload",
        "operation": "manual_upload", "status": "candidate",
        "approval_required": True, "render_required": False,
        "message": "Imagem enviada como alternativa. Aprove-a na galeria para substituir a imagem ativa.",
    }


@router.post("/jobs/{job_id}/scenes/{scene_index}/image-edit")
async def edit_video_job_scene_image(job_id: str, scene_index: int, req: SceneImageEditRequest):
    """Regenerate or text-edit one scene image and attach it to the editable job."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if job_id in _scene_batch_jobs and asyncio.current_task() is not _scene_batch_tasks.get(job_id):
        raise HTTPException(status_code=409, detail="A batch scene regeneration is already running")
    if record.get("_rendering_edits") or record.get("_rebuilding_scene_clips") or record.get("_scene_clip_rebuild_scheduled"):
        raise HTTPException(status_code=409, detail="Scene assets are locked by an active render operation")
    if record.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Scene images can only be changed after generation completes")
    if req.stage_only:
        buckets = record.get("scene_image_candidates")
        existing = buckets.get(str(scene_index), []) if isinstance(buckets, dict) else []
        if isinstance(existing, list) and len(existing) >= 8:
            raise HTTPException(status_code=409, detail="This scene already has the maximum of eight pending image candidates")
    source_scenes = record.get("_edited_scenes") or record.get("_source_scenes") or []
    scenes = [dict(item) for item in source_scenes]
    position = next(
        (i for i, item in enumerate(scenes)
         if int(item.get("_source_scene_index", i)) == scene_index),
        None,
    )
    if position is None and 0 <= scene_index < len(scenes):
        position = scene_index
    if position is None:
        raise HTTPException(status_code=404, detail="Scene index not found")
    from modules.ai_video_studio.media.output_paths import get_subsystem_dir
    from modules.ai_video_studio.ai_image_generator.providers.local_diffusion import (
        edit_image, fit_image_dimensions, generate_scene_image,
    )

    scene = scenes[position]
    params = record.get("params") or {}
    studio_id = str(params.get("studio_id") or "custom")
    style_prompts = {
        "whymentary": "2D educational explainer, clean white background, bold marker-like outlines, flat bright colors",
        "historical_documentary": "cinematic illustrated historical documentary, period-accurate environment, layered depth and atmospheric lighting",
        "felt_clay": "handcrafted felt and clay stop-motion, tactile wool fibers, soft rounded forms, consistent handcrafted materials and warm cinematic lighting",
        "custom": str(scene.get("visual_style") or scene.get("style_prompt") or scene.get("art_direction") or "Follow the user's requested visual direction"),
    }
    if studio_id not in style_prompts:
        raise HTTPException(status_code=422, detail=f"Unsupported visual studio: {studio_id}")
    style_prompt = style_prompts[studio_id]
    character_ids = params.get("character_ids") or []
    edit_prompt = f"{style_prompt}. {req.prompt}"
    image_root = Path(get_subsystem_dir("images")).resolve()
    source_value = scene.get("background_image_path")
    source = Path(str(source_value)).resolve() if source_value else None
    if source is not None and (image_root not in source.parents or not source.is_file()):
        raise HTTPException(status_code=422, detail="Scene source image is not a valid DARKSTUDIO asset")
    try:
        if source is not None:
            result = await asyncio.to_thread(
                edit_image, source, edit_prompt,
                negative_prompt=req.negative_prompt or str(scene.get("negative_prompt") or ""),
                denoising_strength=req.denoising_strength,
                steps=req.steps, cfg_scale=req.cfg_scale, seed=req.seed,
            )
            operation = "image_to_image"
        else:
            params = record.get("params") or {}
            width, height = _parse_resolution(record.get("resolution") or params.get("resolution", "1280x720"))
            image_width, image_height = fit_image_dimensions(width, height)
            result = await asyncio.to_thread(
                generate_scene_image,
                edit_prompt,
                negative_prompt=req.negative_prompt or str(scene.get("negative_prompt") or ""),
                width=image_width,
                height=image_height,
                steps=req.steps, cfg_scale=req.cfg_scale, seed=req.seed,
            )
            operation = "text_to_image"
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if req.stage_only:
        candidate_id = uuid.uuid4().hex
        candidate = {"candidate_id": candidate_id, "scene_index": scene_index,
                     "image_path": result["image_path"], "image_url": to_download_url(result["image_path"]),
                     "provider": result["provider"], "operation": operation, "prompt": req.prompt,
                     "negative_prompt": req.negative_prompt or str(scene.get("negative_prompt") or ""),
                     "seed": result.get("seed", req.seed),
                     "status": "pending_approval"}
        from modules.ai_video_studio.media.scene_visual_asset_workflow import stage_scene_image_candidate
        try:
            updated = stage_scene_image_candidate(record, scene_index, candidate)
        except (ValueError, RuntimeError) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        record.clear()
        record.update(updated)
        _persist_job(record)
        return {"job_id": job_id, "scene_index": scene_index, "candidate_id": candidate_id,
                "image_path": result["image_path"], "image_url": to_download_url(result["image_path"]),
                "operation": operation, "provider": result["provider"], "status": "candidate",
                "prompt": req.prompt, "seed": result.get("seed", req.seed),
                "approval_required": True, "render_required": False}

    scene["background_image_path"] = result["image_path"]
    scene["image_asset_provider"] = result["provider"]
    scene["visual_prompt"] = req.prompt
    scene["visual_prompt_full"] = edit_prompt
    scene["negative_prompt"] = req.negative_prompt or str(scene.get("negative_prompt") or "")
    scene["image_edit_operation"] = operation
    scene["image_generation_seed"] = result.get("seed", req.seed)
    record["_edited_scenes"] = scenes
    assets = record.setdefault("scene_assets", [])
    assets[:] = [item for item in assets if item.get("scene_index") != scene_index]
    assets.append({
        "scene_index": scene_index, "image_path": result["image_path"],
        "image_url": to_download_url(result["image_path"]),
        "provider": result["provider"], "status": "edited",
        "operation": operation, "prompt": req.prompt, "seed": result.get("seed", req.seed),
    })
    record["scene_image_mode"] = "mixed"
    scene_clip_result: dict[str, Any] | None = None
    if record.get("vidgrid_compatible"):
        try:
            from modules.ai_video_studio.media.output_paths import unique_filename
            from modules.ai_video_studio.media.render import render_single_scene_clip

            width, height = _parse_resolution(record.get("resolution") or params.get("resolution", "1280x720"))
            fps = max(1, int(record.get("frame_rate") or params.get("frame_rate") or 24))
            scene["duration"] = 10.0
            clip_path = unique_filename(
                get_subsystem_dir("videos") / "vidgrid_clips",
                f"scene_{scene_index + 1:02d}_edited",
                "mp4",
            )
            rendered_clip = await asyncio.to_thread(
                render_single_scene_clip, scene, clip_path,
                duration=10.0, fps=fps, width=width, height=height,
                require_mp4=True, studio_id=studio_id,
            )
            clip_output_path = rendered_clip["output_path"]
            audio_status = "silent_or_tts_unavailable"
            narration_fingerprint = None
            voiceover = record.get("voiceover")
            voiceover = voiceover if isinstance(voiceover, dict) else {}
            if voiceover.get("narration_style") == "per_scene":
                narration = next(
                    (item for item in voiceover.get("clips", [])
                     if int(item.get("index", -1)) == scene_index and item.get("audio_path")),
                    None,
                )
                if narration:
                    from modules.ai_video_studio.media.audio import mux_audio_into_video

                    try:
                        narration_path = _resolve_scene_narration_asset(narration["audio_path"])
                    except (OSError, ValueError) as narration_exc:
                        raise HTTPException(
                            status_code=422,
                            detail=f"Narração da cena {scene_index + 1} inválida: {narration_exc}",
                        ) from narration_exc

                    voiced_path = unique_filename(
                        get_subsystem_dir("videos") / "vidgrid_clips",
                        f"scene_{scene_index + 1:02d}_edited_voiced",
                        "mp4",
                    )
                    muxed = await asyncio.to_thread(
                        mux_audio_into_video, clip_output_path, narration_path, voiced_path,
                    )
                    if muxed.get("muxed"):
                        clip_output_path = muxed["output_path"]
                        narration_fingerprint = _asset_sha256(Path(narration["audio_path"]).resolve())
                        audio_status = "per_scene_narration_muxed"
                    else:
                        audio_status = "narration_mux_failed"
            elif voiceover.get("narration_style") == "single_track":
                audio_status = "single_track_not_split"
            scene_clip_result = {
                "scene_index": scene_index, "duration": 10.0, "fps": fps,
                "width": width, "height": height, "output_path": clip_output_path,
                "output_url": to_download_url(clip_output_path),
                "bytes": Path(clip_output_path).stat().st_size,
                "encode_engine": rendered_clip["engine"], "audio_status": audio_status,
                "visual_prompt": scene.get("visual_prompt") or scene.get("description", ""),
                "narration_text": scene.get("voiceover_text") or scene.get("narration") or "",
                "status": "updated",
                **({"source_narration_fingerprint": narration_fingerprint} if narration_fingerprint else {}),
            }
            clips = record.setdefault("scene_clips", [])
            clips[:] = [item for item in clips if int(item.get("scene_index", -1)) != scene_index]
            clips.append(scene_clip_result)
            clips.sort(key=lambda item: int(item.get("scene_index", 0)))
        except Exception as exc:  # noqa: BLE001 — image edit remains saved if clip render fails
            scene_clip_result = {"status": "stale", "reason": str(exc)[:240]}
    _persist_job(record)
    return {
        "job_id": job_id, "scene_index": scene_index,
        "image_path": result["image_path"], "image_url": to_download_url(result["image_path"]),
        "operation": operation, "provider": result["provider"],
        "status": "edited", "prompt": req.prompt, "render_required": True,
        "scene_clip": scene_clip_result,
    }






@router.post("/jobs/{job_id}/scenes/{scene_index}/image-candidates/{candidate_id}/discard")
async def discard_video_job_scene_image(job_id: str, scene_index: int, candidate_id: str):
    """Discard one pending candidate without changing the approved image or clip."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if job_id in _scene_batch_jobs or record.get("_rendering_edits") or record.get("_rebuilding_scene_clips") or record.get("_scene_clip_rebuild_scheduled"):
        raise HTTPException(status_code=409, detail="Scene assets are locked by another operation")
    from modules.ai_video_studio.media.scene_visual_asset_workflow import discard_scene_image_candidate
    try:
        updated, _removed = discard_scene_image_candidate(record, scene_index, candidate_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Image candidate not found") from exc
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    record.clear()
    record.update(updated)
    _persist_job(record)
    return {"job_id": job_id, "scene_index": scene_index, "candidate_id": candidate_id,
            "status": "discarded", "active_image_unchanged": True}

@router.post("/jobs/{job_id}/scenes/{scene_index}/image-candidates/{candidate_id}/approve")
async def approve_video_job_scene_image(job_id: str, scene_index: int, candidate_id: str):
    """Promote one reviewed candidate, preserve history and invalidate only its clip."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if job_id in _scene_batch_jobs or record.get("_rendering_edits") or record.get("_rebuilding_scene_clips") or record.get("_scene_clip_rebuild_scheduled"):
        raise HTTPException(status_code=409, detail="Scene assets are locked by another operation")
    if record.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Only completed jobs can approve scene images")

    from modules.ai_video_studio.media.output_paths import get_subsystem_dir
    from modules.ai_video_studio.media.scene_visual_asset_workflow import approve_scene_image_candidate
    image_root = Path(get_subsystem_dir("images")).resolve()
    try:
        updated, candidate = approve_scene_image_candidate(
            record, scene_index, candidate_id,
            image_root=image_root,
            image_url_builder=to_download_url,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Image candidate or scene not found") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    record.clear()
    record.update(updated)
    _persist_job(record)
    image_path = str(Path(str(candidate["image_path"])).resolve())
    image_url = to_download_url(image_path)
    return {
        "job_id": job_id, "scene_index": scene_index, "candidate_id": candidate_id,
        "status": "approved", "image_path": image_path, "image_url": image_url,
        "render_required": True,
        "message": "Imagem aprovada e aplicada. Somente o clipe desta cena ficou desatualizado; reconstrua o clipe VidGrid e depois renderize o MP4 completo.",
    }


def _safe_record_index(value: Any, fallback: int = -1) -> int:
    """Parse persisted scene indices defensively; malformed records must not 500 an audit."""
    try:
        if isinstance(value, bool):
            return fallback
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return fallback


def _asset_health_entry(kind: str, value: Any, allowed_root: Path) -> dict[str, Any]:
    """Inspect one persisted asset reference without exposing absolute paths."""
    if not isinstance(value, (str, Path)) or not str(value).strip():
        return {"kind": kind, "status": "missing", "reason": "path_not_recorded"}
    try:
        path = Path(str(value)).resolve()
        if allowed_root not in path.parents or not path.is_file():
            return {"kind": kind, "status": "missing", "reason": "file_missing_or_outside_asset_root"}
        stat = path.stat()
        if stat.st_size <= 0:
            return {"kind": kind, "status": "corrupt", "reason": "empty_file", "bytes": 0}
        result = {"kind": kind, "status": "available", "bytes": stat.st_size,
                  "sha256": _asset_sha256(path)}
        if kind in {"scene_clip", "scene_narration", "music", "sound_effect"}:
            probe = _probe_media_asset(path, kind)
            if probe.get("status") in {"corrupt", "unreadable"}:
                return {"kind": kind, **probe, "bytes": stat.st_size}
            result.update(probe)
        return result
    except (OSError, ValueError):
        return {"kind": kind, "status": "unreadable", "reason": "file_could_not_be_read"}


def _audio_asset_health(kind: str, value: Any, allowed_root: Path) -> dict[str, Any]:
    """Resolve a timeline audio identifier through the approved audio-asset validator."""
    if not isinstance(value, str) or not value.strip():
        return {"kind": kind, "status": "missing", "reason": "path_not_recorded"}
    try:
        from modules.ai_video_studio.media.audio_timeline import validate_audio_asset
        resolved = validate_audio_asset(value)
    except (OSError, ValueError):
        return {"kind": kind, "status": "missing", "reason": "audio_asset_missing_or_not_approved"}
    return _asset_health_entry(kind, resolved, allowed_root)


def _probe_media_asset(path: Path, kind: str) -> dict[str, Any]:
    """Use FFprobe to validate media containers when the binary is available."""
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return {"probe_status": "not_verified", "probe_reason": "ffprobe_unavailable"}
    try:
        completed = subprocess.run(
            [ffprobe, "-v", "error", "-show_entries",
             "format=duration:stream=codec_type,codec_name,duration,width,height,sample_rate,channels",
             "-of", "json", str(path)],
            capture_output=True, text=True, timeout=20, check=False,
        )
        if completed.returncode != 0:
            return {"status": "corrupt", "reason": "ffprobe_rejected_media",
                    "probe_error": (completed.stderr or "")[:240]}
        metadata = json.loads(completed.stdout or "{}")
        streams = metadata.get("streams") or []
        expected_type = "video" if kind == "scene_clip" else "audio"
        matching = [item for item in streams if item.get("codec_type") == expected_type]
        duration = float((metadata.get("format") or {}).get("duration") or 0)
        if not matching or duration <= 0:
            return {"status": "corrupt", "reason": "expected_stream_or_duration_missing"}
        stream = matching[0]
        details = {"probe_status": "passed", "codec": stream.get("codec_name"),
                   "duration_seconds": duration}
        if expected_type == "video":
            details.update(
                width=stream.get("width"), height=stream.get("height"),
                audio_stream_count=sum(1 for item in streams if item.get("codec_type") == "audio"),
            )
        else:
            details.update(sample_rate=stream.get("sample_rate"), channels=stream.get("channels"))
        return details
    except (OSError, subprocess.TimeoutExpired, ValueError, json.JSONDecodeError):
        return {"status": "unreadable", "reason": "ffprobe_execution_failed"}


@router.get("/jobs/{job_id}/asset-health")
async def get_video_job_asset_health(job_id: str):
    """Audit persisted scene images, VidGrid clips and narration assets, read-only."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    from modules.ai_video_studio.media.output_paths import get_subsystem_dir

    roots = {
        "image": Path(get_subsystem_dir("images")).resolve(),
        "video": Path(get_subsystem_dir("videos")).resolve(),
        "voice": Path(get_subsystem_dir("voice")).resolve(),
        "music": Path(get_subsystem_dir("music")).resolve(),
        "effects": Path(get_subsystem_dir("effects")).resolve(),
    }
    scenes = record.get("_edited_scenes") or record.get("_source_scenes") or []
    clips = {_safe_record_index(item.get("scene_index")): item for item in (record.get("scene_clips") or []) if isinstance(item, dict)}
    voiceover = record.get("voiceover")
    voiceover = voiceover if isinstance(voiceover, dict) else {}
    narration_by_scene = {
        _safe_record_index(item.get("index")): item for item in (voiceover.get("clips") or [])
        if isinstance(item, dict)
    }
    rows: list[dict[str, Any]] = []
    counts = {"available": 0, "missing": 0, "corrupt": 0, "unreadable": 0, "stale": 0}
    for position, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            continue
        scene_index = _safe_record_index(scene.get("_source_scene_index", position), position)
        clip = clips.get(scene_index) or {}
        narration = narration_by_scene.get(scene_index) or {}
        image_asset = _asset_health_entry(
            "scene_image", scene.get("background_image_path"), roots["image"]
        )
        saved_image_fingerprint = clip.get("source_image_fingerprint")
        image_changed = bool(
            saved_image_fingerprint and image_asset.get("sha256")
            and saved_image_fingerprint != image_asset.get("sha256")
        )
        if image_changed or clip.get("status") == "stale":
            image_asset = {
                **image_asset, "status": "stale",
                "reason": "source_image_changed" if image_changed else "clip_marked_stale",
            }
        assets = [
            image_asset,
            _asset_health_entry("scene_clip", clip.get("output_path"), roots["video"]),
        ]
        if voiceover.get("narration_style") == "per_scene":
            narration_asset = _asset_health_entry("scene_narration", narration.get("audio_path"), roots["voice"])
            saved_narration_fingerprint = clip.get("source_narration_fingerprint")
            current_narration_fingerprint = narration_asset.get("sha256")
            if saved_narration_fingerprint and current_narration_fingerprint and saved_narration_fingerprint != current_narration_fingerprint:
                narration_asset = {**narration_asset, "status": "stale", "reason": "source_narration_changed"}
            assets.append(narration_asset)
        for asset in assets:
            counts[asset["status"]] = counts.get(asset["status"], 0) + 1
        rows.append({"scene_index": scene_index, "status": (
            "healthy" if all(item["status"] == "available" for item in assets) else "needs_attention"
        ), "assets": assets})
    audio_clips = record.get("_audio_clips")
    audio_clips = audio_clips if isinstance(audio_clips, dict) else {}
    legacy_audio_settings = record.get("audio_settings")
    legacy_audio_settings = legacy_audio_settings if isinstance(legacy_audio_settings, dict) else {}
    for group, kind, root_key, legacy_key in (
        ("music", "music", "music", "music_clips"),
        ("sfx", "sound_effect", "effects", "sfx_clips"),
    ):
        clip_items = audio_clips.get(group)
        if not isinstance(clip_items, list):
            clip_items = legacy_audio_settings.get(legacy_key) or []
        for position, item in enumerate(clip_items):
            if not isinstance(item, dict):
                item = {}
            asset = _audio_asset_health(kind, item.get("asset"), roots[root_key])
            saved_fingerprint = item.get("asset_fingerprint")
            current_fingerprint = asset.get("sha256")
            if saved_fingerprint and current_fingerprint and saved_fingerprint != current_fingerprint:
                asset = {**asset, "status": "stale", "reason": "asset_changed_since_timeline_save"}
            counts[asset["status"]] = counts.get(asset["status"], 0) + 1
            rows.append({"asset_index": position, "group": group, "status": asset["status"], "assets": [asset]})
    total = sum(counts.values())
    return {
        "job_id": job_id, "status": "healthy" if counts["missing"] + counts["corrupt"] + counts["unreadable"] + counts["stale"] == 0 else "needs_attention",
        "summary": {"total_assets": total, **counts},
        "scenes": rows,
        "checked_at": time.time(),
        "limitations": [
            "A auditoria verifica existência, leitura básica e SHA-256; não comprova qualidade semântica ou sincronização perceptual.",
            "Clipes MP4 não são decodificados quadro a quadro nesta auditoria.",
            "Faixas únicas de narração são reportadas pelo manifesto de áudio, não divididas artificialmente por cena.",
        ],
    }


@router.get("/jobs/{job_id}/dependency-graph")
async def get_video_job_dependency_graph(job_id: str):
    """Describe which generated assets depend on each scene and final export."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    from modules.ai_video_studio.media.output_paths import get_subsystem_dir

    roots = {
        "images": Path(get_subsystem_dir("images")).resolve(),
        "videos": Path(get_subsystem_dir("videos")).resolve(),
        "voice": Path(get_subsystem_dir("voice")).resolve(),
        "music": Path(get_subsystem_dir("music")).resolve(),
        "effects": Path(get_subsystem_dir("effects")).resolve(),
    }
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, str]] = []

    def add_node(node_id: str, node_type: str, label: str, health: dict[str, Any],
                 scene_index: int | None = None) -> None:
        nodes.append({
            "id": node_id, "type": node_type, "label": label,
            "status": health.get("status", "unknown"),
            "reason": health.get("reason"),
            "scene_index": scene_index,
            "bytes": health.get("bytes"),
            "probe_status": health.get("probe_status"),
            "sha256": health.get("sha256"),
        })

    scenes = record.get("_edited_scenes") or record.get("_source_scenes") or []
    clips = {
        _safe_record_index(item.get("scene_index")): item
        for item in (record.get("scene_clips") or []) if isinstance(item, dict)
    }
    voiceover = record.get("voiceover")
    voiceover = voiceover if isinstance(voiceover, dict) else {}
    narration_by_scene = {
        _safe_record_index(item.get("index")): item
        for item in (voiceover.get("clips") or []) if isinstance(item, dict)
    }
    for position, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            continue
        scene_index = _safe_record_index(scene.get("_source_scene_index", position), position)
        image_id = f"scene:{scene_index}:image"
        clip_id = f"scene:{scene_index}:clip"
        image_health = _asset_health_entry(
            "scene_image", scene.get("background_image_path"), roots["images"]
        )
        clip = clips.get(scene_index) or {}
        saved_image_fingerprint = clip.get("source_image_fingerprint")
        image_changed = bool(
            saved_image_fingerprint and image_health.get("sha256")
            and saved_image_fingerprint != image_health.get("sha256")
        )
        if image_changed or clip.get("status") == "stale":
            image_health = {
                **image_health, "status": "stale",
                "reason": "source_image_changed" if image_changed else "clip_marked_stale",
            }
        add_node(image_id, "image", f"Imagem da cena {scene_index + 1}", image_health, scene_index)
        clip_health = _asset_health_entry("scene_clip", clip.get("output_path"), roots["videos"])
        add_node(clip_id, "video_clip", f"Clipe da cena {scene_index + 1}", clip_health, scene_index)
        edges.append({"from": image_id, "to": clip_id, "relationship": "input_for"})
        if voiceover.get("narration_style") == "per_scene":
            narration = narration_by_scene.get(scene_index) or {}
            narration_id = f"scene:{scene_index}:narration"
            narration_health = _asset_health_entry("scene_narration", narration.get("audio_path"), roots["voice"])
            saved_narration_fingerprint = clip.get("source_narration_fingerprint")
            current_narration_fingerprint = narration_health.get("sha256")
            if saved_narration_fingerprint and current_narration_fingerprint and saved_narration_fingerprint != current_narration_fingerprint:
                narration_health = {**narration_health, "status": "stale", "reason": "source_narration_changed"}
            add_node(narration_id, "narration", f"Narração da cena {scene_index + 1}",
                     narration_health, scene_index)
            edges.append({"from": narration_id, "to": clip_id, "relationship": "audio_mux_input"})

    output_id = "final:export"
    output_value = record.get("edited_output_path") or record.get("output_path")
    add_node(output_id, "final_export", "Exportação final",
             _asset_health_entry("final_export", output_value, roots["videos"]))
    for position, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            continue
        scene_index = _safe_record_index(scene.get("_source_scene_index", position), position)
        edges.append({"from": f"scene:{scene_index}:clip", "to": output_id, "relationship": "assembly_input"})

    if voiceover.get("narration_style") != "per_scene" and voiceover.get("output_path"):
        narration_id = "audio:narration"
        add_node(narration_id, "narration_track", "Faixa única de narração",
                 _asset_health_entry("scene_narration", voiceover.get("output_path"), roots["voice"]))
        edges.append({"from": narration_id, "to": output_id, "relationship": "audio_mix_input"})

    audio_clips = record.get("_audio_clips")
    audio_clips = audio_clips if isinstance(audio_clips, dict) else {}
    legacy_audio_settings = record.get("audio_settings")
    legacy_audio_settings = legacy_audio_settings if isinstance(legacy_audio_settings, dict) else {}
    for group, kind, root_key, node_type, legacy_key in (
        ("music", "music", "music", "music", "music_clips"),
        ("sfx", "sound_effect", "effects", "sound_effect", "sfx_clips"),
    ):
        clip_items = audio_clips.get(group)
        if not isinstance(clip_items, list):
            clip_items = legacy_audio_settings.get(legacy_key) or []
        for position, item in enumerate(clip_items):
            if not isinstance(item, dict):
                item = {}
            node_id = f"audio:{group}:{position}"
            health = _audio_asset_health(kind, item.get("asset"), roots[root_key])
            saved_fingerprint = item.get("asset_fingerprint")
            current_fingerprint = health.get("sha256")
            if saved_fingerprint and current_fingerprint and saved_fingerprint != current_fingerprint:
                health = {**health, "status": "stale", "reason": "asset_changed_since_timeline_save"}
            add_node(node_id, node_type, f"{'Música' if kind == 'music' else 'Efeito'} {position + 1}", health)
            edges.append({"from": node_id, "to": output_id, "relationship": "audio_mix_input"})

    status_counts: dict[str, int] = {}
    for node in nodes:
        status_counts[node["status"]] = status_counts.get(node["status"], 0) + 1
    return {
        "job_id": job_id,
        "nodes": nodes,
        "edges": edges,
        "summary": {"nodes": len(nodes), "dependencies": len(edges), "statuses": status_counts},
        "impact_rules": [
            {"changed": "scene_image", "rebuild": ["same_scene_video_clip", "final_export"]},
            {"changed": "scene_narration", "rebuild": ["same_scene_video_clip", "final_export"],
             "condition": "per-scene narration"},
            {"changed": "music_or_sound_effect", "rebuild": ["final_export"]},
        ],
        "limitations": [
            "O grafo representa dependências registradas no job; não detecta dependências externas não registradas.",
            "A exportação final é marcada como dependente dos clipes e faixas de áudio, mas não é reconstruída automaticamente.",
        ],
    }


@router.post("/jobs/{job_id}/dependency-impact")
async def preview_video_job_dependency_impact(job_id: str, req: DependencyImpactRequest):
    """Preview downstream rebuild work for selected persisted assets; never renders."""
    graph = await get_video_job_dependency_graph(job_id)
    nodes_by_id = {node["id"]: node for node in graph["nodes"]}
    unknown = sorted(set(req.changed_asset_ids) - set(nodes_by_id))
    if unknown:
        raise HTTPException(
            status_code=422,
            detail={"message": "Unknown asset IDs for this job", "unknown_asset_ids": unknown},
        )

    outgoing: dict[str, list[str]] = {}
    for edge in graph["edges"]:
        outgoing.setdefault(edge["from"], []).append(edge["to"])

    affected: set[str] = set()
    queue = list(req.changed_asset_ids)
    while queue:
        current = queue.pop(0)
        for downstream in outgoing.get(current, []):
            if downstream not in affected:
                affected.add(downstream)
                queue.append(downstream)

    affected_nodes = [nodes_by_id[node_id] for node_id in nodes_by_id if node_id in affected]
    selected_video_clips = [
        nodes_by_id[node_id] for node_id in req.changed_asset_ids
        if nodes_by_id[node_id].get("type") == "video_clip"
    ]
    impacted_video_clips = [*selected_video_clips, *affected_nodes]
    scene_indices = sorted({
        node["scene_index"] for node in impacted_video_clips
        if node.get("type") == "video_clip" and isinstance(node.get("scene_index"), int)
    })
    final_export_required = any(node["type"] == "final_export" for node in affected_nodes)
    rebuild_steps = []
    if scene_indices:
        rebuild_steps.append({
            "operation": "rebuild_scene_clips",
            "scene_indices": scene_indices,
            "reason": "As cenas selecionadas dependem diretamente de um ou mais ativos alterados",
        })
    if final_export_required:
        rebuild_steps.append({
            "operation": "render_final_export",
            "reason": "A exportação final depende dos ativos alterados ou dos clipes afetados",
        })
    return {
        "job_id": job_id,
        "changed_asset_ids": req.changed_asset_ids,
        "affected_node_ids": [node["id"] for node in affected_nodes],
        "affected_nodes": affected_nodes,
        "rebuild_scene_indices": scene_indices,
        "final_export_required": final_export_required,
        "rebuild_steps": rebuild_steps,
        "requires_user_confirmation": True,
        "executed": False,
        "limitations": [
            "Prévia somente leitura: nenhuma imagem, narração, faixa ou exportação foi alterada.",
            "O plano segue apenas as dependências persistidas no job; recursos externos não registrados podem não aparecer.",
            "A reconstrução seletiva de clipes VidGrid e a renderização final continuam sendo operações separadas.",
        ],
    }


@router.get("/jobs/{job_id}/recovery-plan")
async def get_video_job_recovery_plan(job_id: str):
    """Return a non-destructive, per-scene asset recovery plan."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if record.get("status") not in {"completed", "failed"} or not record.get("vidgrid_compatible"):
        raise HTTPException(status_code=409, detail="Recovery planning requires a completed or partially failed VidGrid job with saved scenes")
    plan = _scene_clip_recovery_plan(record)
    plan["job_id"] = job_id
    plan["full_mp4_render_required"] = bool(plan["repair_scene_indices"])
    return plan


async def _run_scene_clip_rebuild_background(job_id: str, scene_indices: list[int]) -> None:
    record = _jobs.get(job_id)
    if record is None:
        return
    record["_scene_clip_rebuild_scheduled"] = False
    record["_scene_clip_rebuild_worker"] = True
    queue = record.get("scene_clip_rebuild_queue") or {}
    if queue.get("cancel_requested"):
        queue.update({"status": "cancelled", "updated_at": time.time(), "current_scene_index": None})
        record["scene_clip_rebuild_status"] = "cancelled"
        record["_scene_clip_rebuild_worker"] = False
        _persist_job(record)
        return
    queue["status"] = "processing"
    queue["updated_at"] = time.time()
    record["scene_clip_rebuild_queue"] = queue
    try:
        _persist_job(record)
        await rebuild_stale_video_job_scene_clips(
            job_id, SceneClipRebuildRequest(scene_indices=scene_indices)
        )
    except Exception as exc:  # noqa: BLE001
        queue = record.get("scene_clip_rebuild_queue") or {}
        queue.update({
            "status": "failed", "error": str(exc)[:500],
            "updated_at": time.time(), "current_scene_index": None,
        })
        record["scene_clip_rebuild_status"] = "failed"
        _persist_job(record)
    finally:
        record["_scene_clip_rebuild_worker"] = False
        record["_scene_clip_rebuild_scheduled"] = False
        _persist_job(record)


@router.post("/jobs/{job_id}/scenes/rebuild-stale-clips/queue", status_code=202)
async def queue_scene_clip_rebuild(job_id: str, background_tasks: BackgroundTasks, req: SceneClipRebuildRequest | None = None):
    """Schedule selective scene rebuilding and return immediately with a persistent queue id."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if record.get("status") not in {"completed", "failed"} or not record.get("vidgrid_compatible"):
        raise HTTPException(status_code=409, detail="Queued rebuild requires a completed or partially failed VidGrid job")
    if (record.get("_rendering_edits") or record.get("_rebuilding_scene_clips")
        or record.get("_scene_clip_rebuild_scheduled") or job_id in _scene_batch_jobs):
        raise HTTPException(status_code=409, detail="Scene assets are locked by another operation")
    recovery = _scene_clip_recovery_plan(record)
    repairable = sorted(recovery["repair_scene_indices"])
    requested = req.scene_indices if req and req.scene_indices is not None else repairable
    invalid = sorted(set(requested) - set(repairable))
    if invalid:
        raise HTTPException(status_code=422, detail={
            "message": "Only repairable scenes can be queued",
            "invalid_scene_indices": invalid, "repairable_scene_indices": repairable,
        })
    if not requested:
        return {"job_id": job_id, "status": "unchanged", "queued": False, "requested": 0}
    queue_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())
    try:
        from modules.ai_video_studio.media.job_store import enqueue_unique_task_for_job
        inserted = enqueue_unique_task_for_job(
            task_id, "scene_clip_rebuild", job_id, {
                "job_id": job_id, "queue_id": queue_id,
                "scene_indices": list(requested),
            }
        )
        if not inserted:
            raise HTTPException(
                status_code=409,
                detail="A durable scene rebuild task is already queued or leased; wait for worker recovery before resubmitting",
            )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Durable scene rebuild queue is unavailable") from exc

    # No await occurs between durable insertion and publishing the matching
    # in-memory queue, so this process's worker cannot observe a half-created job.
    previous_queue = record.get("scene_clip_rebuild_queue")
    previous_status = record.get("scene_clip_rebuild_status")
    previous_scheduled = record.get("_scene_clip_rebuild_scheduled")
    record["scene_clip_rebuild_queue"] = {
        "queue_id": queue_id, "task_id": task_id,
        "requested_scene_indices": list(requested),
        "total": len(requested), "completed": 0, "failed": 0,
        "current_scene_index": None, "status": "queued", "cancel_requested": False,
        "results": [], "started_at": time.time(), "updated_at": time.time(),
    }
    record["scene_clip_rebuild_status"] = "queued"
    record["_scene_clip_rebuild_scheduled"] = True
    try:
        _persist_job(record)
    except Exception as exc:
        if previous_queue is None:
            record.pop("scene_clip_rebuild_queue", None)
        else:
            record["scene_clip_rebuild_queue"] = previous_queue
        if previous_status is None:
            record.pop("scene_clip_rebuild_status", None)
        else:
            record["scene_clip_rebuild_status"] = previous_status
        if previous_scheduled is None:
            record.pop("_scene_clip_rebuild_scheduled", None)
        else:
            record["_scene_clip_rebuild_scheduled"] = previous_scheduled
        try:
            from modules.ai_video_studio.media.job_store import delete_queued_task
            delete_queued_task(task_id)
        except Exception:
            pass
        raise HTTPException(status_code=503, detail="Could not persist VidGrid rebuild state") from exc
    return {
        "job_id": job_id, "queue_id": queue_id, "task_id": task_id, "status": "queued",
        "queued": True, "requested": len(requested),
        "status_url": f"/videos/jobs/{job_id}/scenes/rebuild-stale-clips/status",
    }


@router.get("/jobs/{job_id}/scenes/rebuild-stale-clips/status")
async def get_scene_clip_rebuild_queue_status(job_id: str):
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    queue = record.get("scene_clip_rebuild_queue")
    if not isinstance(queue, dict):
        raise HTTPException(status_code=404, detail="No scene rebuild queue exists for this job")
    return {"job_id": job_id, **queue}


@router.post("/jobs/{job_id}/scenes/rebuild-stale-clips/cancel")
async def cancel_scene_clip_rebuild_queue(job_id: str):
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    queue = record.get("scene_clip_rebuild_queue")
    if not isinstance(queue, dict) or queue.get("status") not in {"queued", "processing"}:
        raise HTTPException(status_code=409, detail="There is no active scene rebuild to cancel")
    queue["cancel_requested"] = True
    queue["updated_at"] = time.time()
    _persist_job(record)
    return {
        "job_id": job_id, "status": queue.get("status"),
        "cancel_requested": True,
        "message": "Cancellation will take effect after the current scene finishes.",
    }


@router.post("/jobs/{job_id}/scenes/rebuild-stale-clips/resume", status_code=202)
async def resume_scene_clip_rebuild_queue(job_id: str, background_tasks: BackgroundTasks):
    """Resume an interrupted/partial queue using only scenes still marked repairable."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    previous = record.get("scene_clip_rebuild_queue")
    if not isinstance(previous, dict) or previous.get("status") not in {
        "interrupted", "cancelled", "partial", "failed",
    }:
        raise HTTPException(status_code=409, detail="Only interrupted, cancelled or incomplete queues can be resumed")
    # A fresh recovery plan excludes clips that were successfully rebuilt before interruption.
    return await queue_scene_clip_rebuild(job_id, background_tasks, None)


@router.post("/jobs/{job_id}/scenes/rebuild-stale-clips")
async def rebuild_stale_video_job_scene_clips(job_id: str, req: SceneClipRebuildRequest | None = None):
    """Re-render stale VidGrid clips using the currently approved image and narration."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if record.get("status") not in {"completed", "failed"} or not record.get("vidgrid_compatible"):
        raise HTTPException(status_code=409, detail="Selective clip rebuild requires a completed or partially failed VidGrid job")
    if record.get("_rendering_edits") or (record.get("_rebuilding_scene_clips") and not record.get("_scene_clip_rebuild_worker")) or record.get("_scene_clip_rebuild_scheduled") or job_id in _scene_batch_jobs:
        raise HTTPException(status_code=409, detail="Scene assets are locked by another operation")

    scenes = [dict(item) for item in (record.get("_edited_scenes") or record.get("_source_scenes") or [])]
    recovery_plan = _scene_clip_recovery_plan(record)
    repairable = sorted(recovery_plan["repair_scene_indices"])
    requested = req.scene_indices if req and req.scene_indices is not None else repairable
    unknown = sorted(set(requested) - set(repairable))
    if unknown:
        raise HTTPException(
            status_code=422,
            detail={"message": "Only scenes marked repairable can be rebuilt", "invalid_scene_indices": unknown,
                    "repairable_scene_indices": repairable},
        )
    stale = sorted(requested)
    if not stale:
        return {"job_id": job_id, "status": "unchanged", "rebuilt": 0, "failed": 0, "results": []}

    from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
    from modules.ai_video_studio.media.render import render_single_scene_clip
    image_root = Path(get_subsystem_dir("images")).resolve()
    voice_root = Path(get_subsystem_dir("voice")).resolve()
    params = record.get("params") or {}
    try:
        width, height = _parse_resolution(record.get("resolution") or params.get("resolution") or "1280x720")
        fps = int(record.get("frame_rate") or params.get("frame_rate") or 24)
        if not 1 <= fps <= 120:
            raise ValueError("frame_rate must be between 1 and 120")
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    existing_queue = record.get("scene_clip_rebuild_queue")
    existing_queue = existing_queue if isinstance(existing_queue, dict) else {}
    record["_rebuilding_scene_clips"] = True
    record["scene_clip_rebuild_status"] = "processing"
    record["scene_clip_rebuild_queue"] = {
        "queue_id": existing_queue.get("queue_id") if record.get("_scene_clip_rebuild_worker") else None,
        "cancel_requested": bool(existing_queue.get("cancel_requested")) if record.get("_scene_clip_rebuild_worker") else False,
        "requested_scene_indices": list(stale), "total": len(stale), "completed": 0,
        "failed": 0, "current_scene_index": None, "status": "processing",
        "results": [], "started_at": existing_queue.get("started_at") or time.time(),
        "updated_at": time.time(),
    }
    _persist_job(record)
    results: list[dict[str, Any]] = []
    try:
        for scene_index in stale:
            if (record.get("scene_clip_rebuild_queue") or {}).get("cancel_requested"):
                break
            queue = record["scene_clip_rebuild_queue"]
            queue["current_scene_index"] = scene_index
            queue["updated_at"] = time.time()
            queue["results"] = list(results)
            _persist_job(record)
            position = next((i for i, item in enumerate(scenes)
                             if int(item.get("_source_scene_index", i)) == scene_index), None)
            if position is None and 0 <= scene_index < len(scenes):
                position = scene_index
            if position is None:
                results.append({"scene_index": scene_index, "status": "failed", "error": "Scene index not found"})
                continue
            scene = scenes[position]
            image_value = scene.get("background_image_path")
            image_path = Path(str(image_value)).resolve() if image_value else None
            asset_record = next(
                (item for item in (record.get("scene_assets") or [])
                 if isinstance(item, dict) and _safe_record_index(item.get("scene_index")) == scene_index),
                {},
            )
            procedural_source = (
                str(params.get("scene_image_mode") or record.get("scene_image_mode") or "auto") == "procedural"
                or asset_record.get("status") == "fallback"
                or asset_record.get("provider") == "procedural_fallback"
            )
            image_is_safe = bool(
                image_path is not None and image_root in image_path.parents and image_path.is_file()
            )
            if not image_is_safe and not procedural_source:
                results.append({"scene_index": scene_index, "status": "failed", "error": "Approved image missing or outside asset directory"})
                continue
            try:
                scene["duration"] = 10.0
                clip_path = unique_filename(get_subsystem_dir("videos") / "vidgrid_clips",
                                            f"scene_{scene_index + 1:02d}_rebuilt", "mp4")
                rendered = await asyncio.to_thread(
                    render_single_scene_clip, scene, clip_path, duration=10.0, fps=fps,
                    width=width, height=height, require_mp4=True,
                    studio_id=params.get("studio_id") or "custom",
                )
                final_path = rendered["output_path"]
                audio_status = "silent_or_tts_unavailable"
                narration_fingerprint = None
                voiceover = record.get("voiceover")
                voiceover = voiceover if isinstance(voiceover, dict) else {}
                if voiceover.get("narration_style") == "per_scene":
                    narration = next((item for item in voiceover.get("clips", [])
                                      if isinstance(item, dict) and _safe_record_index(item.get("index")) == scene_index
                                      and item.get("audio_path")), None)
                    if narration:
                        narration_path = Path(str(narration["audio_path"])).resolve()
                        if voice_root not in narration_path.parents or not narration_path.is_file():
                            raise ValueError("Scene narration is missing or outside the approved voice asset directory")
                        current_narration_fingerprint = _asset_sha256(narration_path)
                        from modules.ai_video_studio.media.audio import mux_audio_into_video
                        voiced_path = unique_filename(get_subsystem_dir("videos") / "vidgrid_clips",
                                                       f"scene_{scene_index + 1:02d}_rebuilt_voiced", "mp4")
                        muxed = await asyncio.to_thread(mux_audio_into_video, final_path, str(narration_path), voiced_path)
                        if muxed.get("muxed"):
                            final_path = muxed["output_path"]
                            narration_fingerprint = current_narration_fingerprint
                            audio_status = "per_scene_narration_muxed"
                        else:
                            reason = str(muxed.get("reason") or "audio mux failed")[:200]
                            raise ValueError("Scene narration could not be embedded: {}".format(reason))
                clip = {
                    "scene_index": scene_index, "duration": 10.0, "fps": fps,
                    "width": width, "height": height, "output_path": final_path,
                    "output_url": to_download_url(final_path), "bytes": Path(final_path).stat().st_size,
                    "encode_engine": rendered.get("engine"), "audio_status": audio_status,
                    "visual_prompt": scene.get("visual_prompt") or scene.get("description", ""),
                    "narration_text": scene.get("voiceover_text") or scene.get("narration") or "",
                    "status": "updated",
                    "source_image_fingerprint": _asset_sha256(image_path) if image_is_safe and image_path else None,
                    **({"source_narration_fingerprint": narration_fingerprint} if narration_fingerprint else {}),
                }
                clips = record.setdefault("scene_clips", [])
                clips[:] = [item for item in clips if int(item.get("scene_index", -1)) != scene_index]
                clips.append(clip)
                clips.sort(key=lambda item: int(item.get("scene_index", 0)))
                results.append({"scene_index": scene_index, "status": "completed",
                                "output_url": clip["output_url"], "audio_status": audio_status})
            except Exception as exc:  # noqa: BLE001
                results.append({"scene_index": scene_index, "status": "failed", "error": str(exc)[:300]})
            record["scene_clip_rebuild_results"] = list(results)
            queue = record["scene_clip_rebuild_queue"]
            queue["completed"] = sum(item["status"] == "completed" for item in results)
            queue["failed"] = sum(item["status"] == "failed" for item in results)
            queue["results"] = list(results)
            queue["updated_at"] = time.time()
            _persist_job(record)
    finally:
        record["_rebuilding_scene_clips"] = False
        rebuilt = sum(item["status"] == "completed" for item in results)
        cancelled = bool((record.get("scene_clip_rebuild_queue") or {}).get("cancel_requested"))
        record["scene_clip_rebuild_status"] = (
            "cancelled" if cancelled else
            "completed" if rebuilt == len(stale) else "partial" if rebuilt else "failed"
        )
        queue = record.get("scene_clip_rebuild_queue") or {}
        queue.update({
            "status": record["scene_clip_rebuild_status"], "current_scene_index": None,
            "completed": rebuilt, "failed": len(results) - rebuilt,
            "results": list(results), "updated_at": time.time(),
        })
        _persist_job(record)

    rebuilt = sum(item["status"] == "completed" for item in results)
    return {
        "job_id": job_id, "status": record["scene_clip_rebuild_status"],
        "requested": len(stale), "rebuilt": rebuilt, "failed": len(results) - rebuilt,
        "queue": record.get("scene_clip_rebuild_queue"),
        "results": results, "full_mp4_render_required": True,
        "message": f"{rebuilt} de {len(stale)} clipes regenerados reutilizando imagens aprovadas e narração existente. O MP4 completo ainda precisa ser renderizado.",
    }


@router.post("/jobs/{job_id}/scenes/regenerate")
async def regenerate_video_job_scene_images(job_id: str, req: SceneImageBatchEditRequest):
    """Regenerate selected scene images sequentially; preserve per-scene outcomes."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if record.get("_rendering_edits") or record.get("_rebuilding_scene_clips") or record.get("_scene_clip_rebuild_scheduled"):
        raise HTTPException(status_code=409, detail="Scene assets are locked by an active render operation")
    if record.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Scene images can only be changed after generation completes")
    if job_id in _scene_batch_jobs:
        raise HTTPException(status_code=409, detail="A batch scene regeneration is already running")
    indices = [item.scene_index for item in req.scenes]
    if len(indices) != len(set(indices)):
        raise HTTPException(status_code=422, detail="Duplicate scene indices are not allowed")

    _scene_batch_jobs.add(job_id)
    current_task = asyncio.current_task()
    if current_task is not None:
        _scene_batch_tasks[job_id] = current_task
    record["_scene_batch_total"] = len(req.scenes)
    record["_scene_batch_completed"] = 0
    _persist_job(record)
    results: list[dict[str, Any]] = []
    try:
        for item in req.scenes:
            try:
                result = await edit_video_job_scene_image(
                    job_id, item.scene_index,
                    SceneImageEditRequest(
                        prompt=item.prompt,
                        negative_prompt=item.negative_prompt,
                        seed=item.seed,
                        stage_only=True,
                    ),
                )
                results.append({"scene_index": item.scene_index, "status": "candidate", "result": result})
            except HTTPException as exc:
                results.append({
                    "scene_index": item.scene_index,
                    "status": "failed",
                    "error": str(exc.detail),
                    "http_status": exc.status_code,
                })
            except Exception as exc:  # noqa: BLE001 — report failure without losing completed scenes
                results.append({
                    "scene_index": item.scene_index,
                    "status": "failed",
                    "error": str(exc)[:300],
                })
            finally:
                record["_scene_batch_completed"] = len(results)
                _persist_job(record)
    finally:
        _scene_batch_tasks.pop(job_id, None)
        _scene_batch_jobs.discard(job_id)
        _persist_job(record)

    succeeded = sum(item["status"] == "candidate" for item in results)
    return {
        "job_id": job_id,
        "status": "completed" if succeeded == len(results) else "partial" if succeeded else "failed",
        "requested": len(results),
        "succeeded": succeeded,
        "failed": len(results) - succeeded,
        "results": results,
        "message": f"{succeeded} de {len(results)} imagens geradas como candidatas. Compare e aprove cada uma antes de renderizar.",
    }


@router.post("/jobs/{job_id}/scenes/{scene_index}/motion")
async def generate_video_job_scene_motion(job_id: str, scene_index: int, req: SceneMotionRequest):
    """Generate and persist a ComfyUI MP4 as the visual source for one timeline scene."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if record.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Scene motion can only be generated for completed jobs")

    scenes = record.get("_edited_scenes") or record.get("_source_scenes") or []
    position = next(
        (i for i, item in enumerate(scenes)
         if int(item.get("_source_scene_index", i)) == scene_index),
        None,
    )
    if position is None and 0 <= scene_index < len(scenes):
        position = scene_index
    if position is None:
        raise HTTPException(status_code=404, detail="Scene index not found")

    from modules.ai_video_studio.media.output_paths import get_subsystem_dir
    image_root = Path(get_subsystem_dir("images")).resolve()
    scene = dict(scenes[position])
    image_value = scene.get("background_image_path")
    if not image_value:
        asset = next(
            (item for item in record.get("scene_assets", [])
             if int(item.get("scene_index", -1)) == scene_index and item.get("image_path")),
            None,
        )
        image_value = asset.get("image_path") if asset else None
    image_path = Path(str(image_value)).resolve() if image_value else None
    if image_path is None or image_root not in image_path.parents or not image_path.is_file():
        raise HTTPException(status_code=422, detail="A valid DARKSTUDIO scene image is required before generating motion")

    params = record.get("params") or {}
    try:
        width, height = _parse_resolution(params.get("resolution") or record.get("resolution") or "1280x720")
        fps = int(params.get("frame_rate") or record.get("frame_rate") or 24)
        duration = 10.0 if record.get("vidgrid_compatible") else float(scene.get("duration") or 3.0)
        from modules.ai_video_studio.ai_video_generator.image_to_video.image_to_video_engine import ImageToVideoEngine
        result = await asyncio.to_thread(
            ImageToVideoEngine().generate,
            {
                "id": f"{job_id}-scene-{scene_index}",
                "prompt": str(image_path),
                "params": {
                    "duration": duration, "fps": fps, "width": width, "height": height,
                    "motion_provider": "comfyui", "motion_prompt": req.motion_prompt,
                    "negative_prompt": req.negative_prompt, "provider_timeout": req.provider_timeout,
                },
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        from modules.ai_video_studio.core.exceptions import VideoStudioError
        if isinstance(exc, VideoStudioError):
            raise HTTPException(status_code=exc.status_code, detail=exc.to_dict()) from exc
        raise HTTPException(status_code=502, detail=f"ComfyUI scene generation failed: {str(exc)[:300]}") from exc

    scene["generative_video_path"] = result["output_path"]
    scene["generative_video_provider"] = result.get("provider", "comfyui_workflow")
    scene["generative_video_prompt"] = req.motion_prompt
    scene["generative_video_metadata"] = {
        "provider_prompt_id": result.get("provider_prompt_id"),
        "duration": result.get("duration"),
        "fps": result.get("fps"),
        "frames": result.get("frames"),
        "width": width,
        "height": height,
        "source_image": str(image_path),
    }
    edited = [dict(item) for item in scenes]
    edited[position] = scene
    record["_edited_scenes"] = edited

    clip_records = record.setdefault("scene_clips", [])
    existing = next((item for item in clip_records if int(item.get("scene_index", -1)) == scene_index), None)
    if existing is None:
        existing = {"scene_index": scene_index}
        clip_records.append(existing)
    existing.update({
        "generative_video_path": result["output_path"],
        "generative_video_url": to_download_url(result["output_path"]),
        "generative_video_provider": result.get("provider", "comfyui_workflow"),
        "generative_video_prompt": req.motion_prompt,
        "generative_video_duration": result.get("duration"),
        "generative_video_frames": result.get("frames"),
        "generative_video_fps": result.get("fps"),
        "generative_video_status": "ready",
    })
    clip_records.sort(key=lambda item: int(item.get("scene_index", 0)))
    record["edit_render_status"] = None
    _persist_job(record)
    return {
        "job_id": job_id, "scene_index": scene_index, "status": "ready",
        "provider": result.get("provider"), "provider_prompt_id": result.get("provider_prompt_id"),
        "duration": result.get("duration"), "frames": result.get("frames"), "fps": result.get("fps"),
        "output_path": result["output_path"], "download_url": to_download_url(result["output_path"]),
        "message": "Clipe generativo salvo na cena do projeto e será usado no próximo render da timeline.",
    }


@router.post("/images/edit")
async def edit_generated_scene_image(req: ImageEditRequest):
    """Apply a text instruction to an existing DARKSTUDIO image asset."""
    from modules.ai_video_studio.media.output_paths import get_subsystem_dir
    from modules.ai_video_studio.ai_image_generator.providers.local_diffusion import edit_image

    image_root = Path(get_subsystem_dir("images")).resolve()
    source = Path(req.source_path).resolve()
    if image_root not in source.parents or not source.is_file():
        raise HTTPException(status_code=422, detail="A source image from the DARKSTUDIO image library is required")
    try:
        result = await asyncio.to_thread(
            edit_image,
            source,
            req.prompt,
            negative_prompt=req.negative_prompt,
            denoising_strength=req.denoising_strength,
            steps=req.steps,
            cfg_scale=req.cfg_scale,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {
        **result,
        "image_url": to_download_url(result["image_path"]),
        "source_url": to_download_url(str(source)),
    }


@router.post("/preflight")
async def preflight_video_generation(req: VideoGenerateRequest):
    """Check local prerequisites before queueing a video job.

    This is a configuration check, not a guarantee that an external model
    will be reachable or produce a successful result.
    """
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    image_api = os.getenv("DARKSTUDIO_IMAGE_API_URL", "http://127.0.0.1:7860").strip()
    image_api_available, image_api_error = await asyncio.to_thread(_probe_image_api, image_api)
    comfy_url = os.getenv("DARKSTUDIO_COMFYUI_URL", "").strip()
    comfy_workflow = os.getenv("DARKSTUDIO_COMFYUI_WORKFLOW", "").strip()
    workflow_exists = bool(comfy_workflow and Path(comfy_workflow).is_file())

    if image_api_available:
        image_status = "ready"
        image_message = f"Gerador de imagens acessível em {image_api}."
    elif req.scene_image_mode == "ai":
        image_status = "blocked"
        image_message = image_api_error or "O modo IA exige um gerador de imagens acessível."
    elif req.scene_image_mode == "auto":
        image_status = "warning"
        image_message = (image_api_error or "Gerador de imagens indisponível.") + " O modo automático poderá usar imagens procedurais."
    else:
        image_status = "optional"
        image_message = (image_api_error or "Gerador de imagens indisponível.") + " O modo procedural não depende dele."

    checks = [
        {"id": "ffmpeg", "status": "ready" if ffmpeg else "blocked",
         "message": f"FFmpeg encontrado: {ffmpeg}" if ffmpeg else "FFmpeg não encontrado no PATH; a exportação MP4 não pode ser concluída."},
        {"id": "ffprobe", "status": "ready" if ffprobe else "warning",
         "message": "FFprobe disponível para validar duração e metadados." if ffprobe else "FFprobe ausente; a duração final pode ficar sem confirmação automática."},
        {"id": "image_provider", "status": image_status, "message": image_message},
        {"id": "generative_video", "status": "ready" if comfy_url and workflow_exists else "optional",
         "message": "ComfyUI e workflow configurados; conexão não testada." if comfy_url and workflow_exists else "ComfyUI não está completamente configurado; movimentos de câmera continuam disponíveis."},
    ]
    blockers = [item for item in checks if item["status"] == "blocked"]
    warnings = [item["message"] for item in checks if item["status"] in {"warning", "missing", "optional", "configured_unverified"}]
    if req.voiceover:
        warnings.append("A disponibilidade do mecanismo TTS e da voz será confirmada durante a síntese.")
    total_seconds = req.num_scenes * 10 if req.vidgrid_compatible else req.duration_seconds
    clip_seconds = 10 if req.vidgrid_compatible else None
    width, height = _parse_resolution(req.resolution)
    if width * height >= 1920 * 1080 and req.frame_rate >= 30:
        warnings.append("Resolução/FPS elevados podem tornar a renderização lenta em hardware de entrada.")
    return {
        "status": "blocked" if blockers else ("ready_with_warnings" if warnings else "ready"),
        "can_queue": not blockers, "project_id": req.project_id, "studio_id": req.studio_id,
        "scene_count": req.num_scenes, "duration_seconds": total_seconds,
        "clip_duration_seconds": clip_seconds, "total_frames": int(total_seconds * req.frame_rate),
        "resolution": f"{width}x{height}", "fps": req.frame_rate,
        "vidgrid_compatible": req.vidgrid_compatible, "checks": checks,
        "blockers": blockers, "warnings": warnings,
        "limitations": [
            "O preflight verifica configuração local, não garante disponibilidade remota nem qualidade artística.",
            "O modo de imagem IA gera imagens estáticas por cena; movimento generativo depende de workflow ComfyUI.",
        ],
    }
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
        "scene_progress": [],
        "vidgrid_compatible": req.vidgrid_compatible,
        "clip_duration_seconds": 10.0 if req.vidgrid_compatible else None,
        "scene_image_mode": req.scene_image_mode,
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
            last_persisted_frames = 0
            last_persisted_at = time.monotonic()

            def _on_render_progress(rendered: int, total: int) -> None:
                nonlocal last_persisted_frames, last_persisted_at
                record["frames_rendered"] = rendered
                record["total_frames"] = total
                record["current_step"] = "Rendering frames"
                if total > 0:
                    record["progress"] = 0.1 + 0.75 * min(rendered, total) / total
                now = time.monotonic()
                # Persist an occasional checkpoint without forcing a SQLite
                # transaction for every encoded frame. A first checkpoint and
                # the final frame are always saved.
                should_persist = (
                    last_persisted_frames == 0
                    or rendered >= total
                    or rendered - last_persisted_frames >= max(1, r.frame_rate * 2)
                    or now - last_persisted_at >= 2.0
                )
                if should_persist:
                    try:
                        _persist_job(record)
                        last_persisted_frames = rendered
                        last_persisted_at = now
                    except Exception as persist_error:  # noqa: BLE001
                        # A transient checkpoint failure must not abort FFmpeg.
                        record["progress_persistence_warning"] = str(persist_error)[:240]

            def _on_scene_progress(event: dict[str, Any]) -> None:
                index = int(event.get("scene_index", -1))
                if index < 0:
                    return
                items = list(record.get("scene_progress") or [])
                while len(items) <= index:
                    items.append({"scene_index": len(items), "status": "pending", "stage": "queued"})
                items[index] = {**items[index], **{key: value for key, value in event.items() if key != "scene_snapshot"}}
                record["scene_progress"] = items
                _merge_scene_checkpoint(record, event)
                record["current_step"] = (
                    f"Cena {index + 1}: {str(event.get('stage') or 'processando').replace('_', ' ')}"
                )
                try:
                    _persist_job(record)
                except Exception as persist_error:  # noqa: BLE001
                    record["progress_persistence_warning"] = str(persist_error)[:240]

            result = await TextToVideoEngine().generate_async(
                {
                    "id": job_id,
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
                        "style": r.style,
                        "character_ids": r.character_ids,
                        "object_ids": r.object_ids,
                        "scene_image_mode": r.scene_image_mode,
                        "scene_image_steps": r.scene_image_steps,
                        "scene_image_seed": r.scene_image_seed,
                        "scene_image_timeout": r.scene_image_timeout,
                        "vidgrid_compatible": r.vidgrid_compatible,
                    },
                },
                progress_callback=_on_render_progress,
                scene_callback=_on_scene_progress,
            )
            output_path = result["output_path"]
            subtitle_info = result.get("subtitles")
            if isinstance(subtitle_info, dict) and subtitle_info.get("file_path"):
                subtitle_info = {
                    **subtitle_info,
                    "download_url": to_download_url(subtitle_info["file_path"]),
                }
            scene_assets = result.get("scene_assets") or []
            for asset in scene_assets:
                if asset.get("image_path") and asset.get("status") in {"generated", "edited"}:
                    asset["image_url"] = to_download_url(asset["image_path"])
            scene_clips = result.get("scene_clips") or []
            for clip in scene_clips:
                clip["output_url"] = to_download_url(clip["output_path"])
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
                scene_image_mode=result.get("scene_image_mode", "procedural"),
                scene_assets=result.get("scene_assets", []),
                storyboard_report=result.get("storyboard_report"),
                vidgrid_compatible=result.get("vidgrid_compatible", False),
                clip_duration_seconds=result.get("clip_duration_seconds"),
                scene_clips=scene_clips,
                scene_progress=[
                    {**item, "status": "completed", "stage": "exported"}
                    for item in (record.get("scene_progress") or [])
                ],
                _source_scenes=result.get("scenes"),
                _edited_scenes=result.get("scenes"),
            )
            await _persist_output_validation(job_id)
            _persist_job(record)
        except Exception as e:  # noqa: BLE001 — surface any failure on the job
            progress_items = list(record.get("scene_progress") or [])
            active = next((item for item in reversed(progress_items) if item.get("status") == "processing"), None)
            if active is not None:
                active["status"] = "failed"
                active["stage"] = "failed"
                active["error"] = str(e)[:300]
            completed_indices = [
                int(item.get("scene_index", index))
                for index, item in enumerate(progress_items)
                if item.get("status") == "completed"
            ]
            failed_scene = next(
                (item for item in reversed(progress_items) if item.get("status") == "failed"),
                None,
            )
            failed_stage = str(
                (failed_scene or {}).get("stage")
                or record.get("current_step")
                or "generation"
            )
            record.update(
                status="failed",
                error=str(e),
                scene_progress=progress_items,
                failure_info={
                    "kind": "generation_error",
                    "failed_stage": failed_stage,
                    "failed_scene_index": failed_scene.get("scene_index") if failed_scene else None,
                    "last_completed_scene_index": max(completed_indices) if completed_indices else None,
                    "completed_scene_indices": completed_indices,
                    "automatic_resume_supported": False,
                    "recovery_hint": (
                        "O job preservou o diagnóstico e o progresso de cenas. "
                        "A retomada automática da geração inicial ainda não está disponível."
                    ),
                },
            )
            _persist_job(record)

    background_tasks.add_task(_run, job_id, req)
    return VideoGenerateResponse(
        job_id=job_id,
        project_id=req.project_id,
        status="queued",
        estimated_seconds=(req.num_scenes * 10.0 if req.vidgrid_compatible else req.duration_seconds) * 2,
        message="Video generation queued",
        format=req.format,
    )


@router.post("/jobs/{job_id}/resume-generation", status_code=202)
async def resume_interrupted_generation(job_id: str, background_tasks: BackgroundTasks):
    """Resume a failed generation from its complete saved storyboard and assets."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if record.get("status") not in {"failed", "interrupted"}:
        raise HTTPException(status_code=409, detail="Only failed or interrupted generation jobs can be resumed")
    scenes = [
        dict(item) for item in (record.get("_source_scenes") or [])
        if isinstance(item, dict) and item
    ]
    params = dict(record.get("params") or {})
    expected = int(params.get("num_scenes") or len(scenes) or 0)
    if expected <= 0 or len(scenes) != expected:
        raise HTTPException(
            status_code=409,
            detail="The saved storyboard is incomplete. This job cannot be resumed safely; create a new generation.",
        )
    if record.get("_generation_resume_scheduled"):
        raise HTTPException(status_code=409, detail="A generation recovery is already queued")

    params["checkpoint_scenes"] = scenes
    params["checkpoint_scene_assets"] = [
        dict(item) for item in (record.get("scene_assets") or []) if isinstance(item, dict)
    ]
    record["_generation_resume_scheduled"] = True
    record.update(
        status="queued", progress=0.0, current_step="Preparing saved storyboard recovery",
        error=None, failure_info=None,
    )
    _persist_job(record)

    async def _resume() -> None:
        record["_generation_resume_scheduled"] = False
        record.update(status="processing", progress=0.05, current_step="Reusing saved storyboard")
        _persist_job(record)
        try:
            from modules.ai_video_studio.ai_video_generator.text_to_video.text_to_video_engine import TextToVideoEngine

            width, height = _parse_resolution(str(params.get("resolution") or record.get("resolution") or "1280x720"))
            engine_params = {
                "duration": params.get("duration_seconds", params.get("duration", 6.0)),
                "num_scenes": expected,
                "fps": params.get("frame_rate", record.get("frame_rate", 24)),
                "width": width, "height": height,
                "voiceover": params.get("voiceover", False),
                "generate_subtitles": params.get("generate_subtitles", False),
                "voice_id": params.get("voice_id"),
                "voice_language": params.get("voice_language"),
                "voice_speed": params.get("voice_speed"),
                "voice_pitch": params.get("voice_pitch"),
                "voiceover_mode": params.get("voiceover_mode"),
                "llm_timeout": params.get("llm_timeout", 60.0),
                "studio_id": params.get("studio_id", "custom"),
                "style": params.get("style", ""),
                "character_ids": params.get("character_ids") or [],
                "object_ids": params.get("object_ids") or [],
                "scene_image_mode": params.get("scene_image_mode", "auto"),
                "scene_image_steps": params.get("scene_image_steps", 20),
                "scene_image_seed": params.get("scene_image_seed"),
                "scene_image_timeout": params.get("scene_image_timeout", 180),
                "vidgrid_compatible": params.get("vidgrid_compatible", record.get("vidgrid_compatible", False)),
                "checkpoint_scenes": scenes,
                "checkpoint_scene_assets": params["checkpoint_scene_assets"],
                "checkpoint_narration_clips": [
                    dict(item) for item in ((record.get("voiceover") or {}).get("clips") or [])
                    if isinstance(item, dict)
                ],
                "checkpoint_scene_clips": [
                    dict(item) for item in (record.get("scene_clips") or [])
                    if isinstance(item, dict)
                ],
            }

            def on_narration_clip(clip: dict[str, Any]) -> None:
                # Persist each synthesized/reused narration clip immediately so
                # an interrupted recovery can resume without repeating TTS.
                voiceover = dict(record.get("voiceover") or {})
                clips = [
                    dict(item) for item in (voiceover.get("clips") or [])
                    if isinstance(item, dict)
                    and int(item.get("index", -1)) != int(clip.get("index", -2))
                ]
                clips.append(dict(clip))
                clips.sort(key=lambda item: int(item.get("index", 0)))
                voiceover.update(
                    clips=clips,
                    narration_style="per_scene",
                    checkpoint_status="in_progress",
                )
                record["voiceover"] = voiceover
                _persist_job(record)

            engine_params["narration_clip_callback"] = on_narration_clip

            def on_scene(event: dict[str, Any]) -> None:
                index = int(event.get("scene_index", -1))
                if index < 0:
                    return
                progress = list(record.get("scene_progress") or [])
                while len(progress) <= index:
                    progress.append({"scene_index": len(progress), "status": "pending", "stage": "queued"})
                progress[index] = {
                    **progress[index],
                    **{key: value for key, value in event.items() if key != "scene_snapshot"},
                }
                record["scene_progress"] = progress
                _merge_scene_checkpoint(record, event)
                record["current_step"] = f"Recuperando cena {index + 1}: {event.get('stage', 'processando')}"
                _persist_job(record)

            result = await TextToVideoEngine().generate_async(
                {"id": job_id, "prompt": str(params.get("prompt") or record.get("prompt") or ""), "params": engine_params},
                scene_callback=on_scene,
            )
            scene_assets = result.get("scene_assets") or []
            for asset in scene_assets:
                if asset.get("image_path") and asset.get("status") in {"generated", "edited", "preserved"}:
                    asset["image_url"] = to_download_url(asset["image_path"])
            scene_clips = result.get("scene_clips") or []
            for clip in scene_clips:
                clip["output_url"] = to_download_url(clip["output_path"])
            record.update(
                status="completed", progress=1.0, current_step="Recovery complete",
                output_path=result["output_path"], output_url=to_download_url(result["output_path"]),
                file_size_bytes=result.get("output_bytes", 0),
                ai_planner=result.get("ai_planner"),
                video_duration=await _probe_video_duration(result["output_path"]),
                voiceover=result.get("voiceover"), subtitles=result.get("subtitles"),
                edit_timeline=result.get("edit_timeline"), scene_assets=scene_assets,
                scene_clips=scene_clips, storyboard_report=result.get("storyboard_report"),
                vidgrid_compatible=result.get("vidgrid_compatible", False),
                _source_scenes=result.get("scenes"), _edited_scenes=result.get("scenes"),
                failure_info=None, error=None,
            )
            await _persist_output_validation(job_id)
            _persist_job(record)
        except Exception as exc:  # noqa: BLE001
            # A failed retry must not hide which checkpoints survived. Re-scan
            # the approved asset roots after the exception and persist that
            # factual recovery snapshot alongside the failure reason.
            try:
                from modules.ai_video_studio.media.job_store import _inspect_recoverable_scene_assets

                preserved_assets = _inspect_recoverable_scene_assets(record)
            except Exception:  # noqa: BLE001
                preserved_assets = {
                    "preserved_image_count": 0,
                    "preserved_clip_count": 0,
                    "preserved_narration_count": 0,
                    "recoverable_scene_indices": [],
                    "scene_assets_preserved": False,
                    "inspection_error": "asset_recovery_inspection_failed",
                }
            record.update(
                status="failed", error=str(exc),
                failure_info={
                    "kind": "generation_recovery_error",
                    "automatic_resume_supported": True,
                    **preserved_assets,
                    "recovery_hint": (
                        "A tentativa falhou, mas os arquivos de checkpoint listados neste relatório "
                        "foram verificados e preservados. Corrija a causa e tente recuperar novamente."
                        if preserved_assets.get("scene_assets_preserved")
                        else "A tentativa falhou. O storyboard foi mantido; verifique os assets e tente recuperar novamente."
                    ),
                },
            )
            _persist_job(record)

    background_tasks.add_task(_resume)
    return {
        "job_id": job_id, "status": "queued", "queued": True,
        "reused_scene_count": len(scenes),
        "message": "A geração será refeita usando o storyboard e as imagens salvas, sem novo planejamento visual.",
    }



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
    if record.get("vidgrid_compatible"):
        expected_frames = fps * 10
        invalid_durations = [
            item.scene_index for item in req.scene_edits
            if item.duration_frames is not None and item.duration_frames != expected_frames
        ]
        if invalid_durations:
            raise HTTPException(
                status_code=422,
                detail=f"VidGrid mode requires exactly 10 seconds ({expected_frames} frames) per scene; invalid scenes: {invalid_durations}",
            )
    try:
        source_scenes = record["_source_scenes"]
        # Rebuild the source-order storyboard from the latest edited draft so
        # image edits and persisted ComfyUI MP4s survive subsequent timeline saves.
        base_by_source = {index: dict(scene) for index, scene in enumerate(source_scenes)}
        for position, current_scene in enumerate(record.get("_edited_scenes") or []):
            source_index = int(current_scene.get("_source_scene_index", position))
            if 0 <= source_index < len(source_scenes):
                base_by_source[source_index] = dict(current_scene)
        base_scenes = [base_by_source[index] for index in range(len(source_scenes))]
        edited = apply_scene_edits(
            base_scenes,
            scene_order=req.scene_order,
            scene_edits=[item.model_dump(exclude_none=True) for item in req.scene_edits],
            fps=fps,
        )
        width, height = _parse_resolution(params.get("resolution") or record.get("resolution") or "1280x720")
        audio_drafts = record.get("_audio_clips") or {}
        timeline = build_edit_timeline(
            edited,
            fps=fps,
            width=width,
            height=height,
            music_clips=audio_drafts.get("music", []),
            sfx_clips=audio_drafts.get("sfx", []),
        )
        previous = record.get("edit_timeline") or {}
        timeline["tracks"].extend(
            track for track in previous.get("tracks", [])
            if track.get("type") != "video" and track.get("role") not in {"music", "sound_effect"}
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    record["_edited_scenes"] = edited
    record["edit_timeline"] = timeline
    record["edit_draft_status"] = "saved"
    record["edit_render_quality"] = None
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


@router.get("/jobs/{job_id}/scene-narration/{scene_index}/audio")
async def get_video_job_scene_narration_audio(job_id: str, scene_index: int):
    """Stream one persisted per-scene narration file for review in the editor."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if scene_index < 0:
        raise HTTPException(status_code=422, detail="scene_index must be zero or greater")
    voiceover = record.get("voiceover")
    if not isinstance(voiceover, dict) or voiceover.get("narration_style") != "per_scene":
        raise HTTPException(status_code=409, detail="This job does not contain per-scene narration")
    clips = voiceover.get("clips")
    clip = next((item for item in clips if isinstance(item, dict) and item.get("index") == scene_index), None) if isinstance(clips, list) else None
    if not clip or not clip.get("audio_path"):
        raise HTTPException(status_code=404, detail=f"Narration audio for scene {scene_index + 1} was not found")

    from modules.ai_video_studio.media.output_paths import get_subsystem_dir
    voice_root = Path(get_subsystem_dir("voice")).resolve()
    try:
        audio_path = Path(str(clip["audio_path"])).expanduser().resolve(strict=True)
        if voice_root not in audio_path.parents or not audio_path.is_file() or audio_path.stat().st_size <= 0:
            raise ValueError("invalid narration asset")
    except (OSError, RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=404, detail="Narration audio is missing or unavailable") from exc

    media_types = {".mp3": "audio/mpeg", ".wav": "audio/wav", ".m4a": "audio/mp4", ".ogg": "audio/ogg", ".flac": "audio/flac"}
    return FileResponse(audio_path, media_type=media_types.get(audio_path.suffix.lower(), "application/octet-stream"), filename=audio_path.name)


@router.post("/jobs/{job_id}/scene-narration/{scene_index}/regenerate")
async def regenerate_video_job_scene_narration(
    job_id: str, scene_index: int, req: SceneNarrationRegenerateRequest
):
    """Regenerate only one scene's narration; keep the previous file for rollback."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if scene_index < 0:
        raise HTTPException(status_code=422, detail="scene_index must be zero or greater")
    if record.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Narration can only be changed after generation completes")
    if (record.get("_rendering_edits") or record.get("_rebuilding_scene_clips")
            or record.get("_scene_clip_rebuild_scheduled") or job_id in _scene_batch_jobs):
        raise HTTPException(status_code=409, detail="Scene assets are locked by another operation")

    voiceover = record.get("voiceover")
    if not isinstance(voiceover, dict) or voiceover.get("narration_style") != "per_scene":
        raise HTTPException(status_code=409, detail="Individual narration regeneration requires per-scene narration")
    clips = voiceover.get("clips")
    clip = next(
        (item for item in clips if isinstance(item, dict) and _safe_record_index(item.get("index"), -1) == scene_index),
        None,
    ) if isinstance(clips, list) else None
    if clip is None:
        raise HTTPException(status_code=404, detail=f"Narration scene {scene_index + 1} was not found")

    from modules.ai_video_studio.media.output_paths import get_subsystem_dir
    voice_root = Path(get_subsystem_dir("voice")).resolve()
    voice_root.mkdir(parents=True, exist_ok=True)
    params = record.get("params") or {}
    voice_id = req.voice_id or voiceover.get("voice_id") or params.get("voice_id") or "default"
    language = req.language or voiceover.get("language") or params.get("voice_language") or "pt-BR"
    speed = req.speed if req.speed is not None else float(params.get("voice_speed") or 1.0)
    pitch = req.pitch if req.pitch is not None else float(params.get("voice_pitch") or 1.0)
    output_path = voice_root / f"job_{job_id}_scene_{scene_index + 1:02d}_{uuid.uuid4().hex}.mp3"

    from modules.ai_video_studio.services.voice_studio import VoiceStudioService
    from modules.ai_video_studio.core.exceptions import AIError
    try:
        result = await VoiceStudioService().synthesize(
            req.text, voice_id=voice_id, language=language, speed=speed,
            pitch=pitch, emotion=req.emotion, output_path=str(output_path),
        )
    except AIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.to_dict()) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Narration synthesis failed: {str(exc)[:240]}") from exc

    try:
        generated_path = Path(str(result.get("file_path") or "")).resolve(strict=True)
        if (voice_root not in generated_path.parents or not generated_path.is_file()
                or generated_path.stat().st_size <= 0):
            raise ValueError("TTS returned an empty or unsafe narration file")
        duration = float(result.get("duration") or 0)
        if duration <= 0:
            raise ValueError("TTS output duration could not be verified")
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=f"Generated narration failed validation: {str(exc)[:200]}") from exc

    # Keep the old asset on disk. Only replace the selected scene's source
    # reference; the recovery planner's narration fingerprint will mark its
    # already-muxed MP4 clip stale without touching the other scenes.
    previous_path = clip.get("audio_path")
    previous_clip = dict(clip)
    previous_fields = {
        key: (key in record, record.get(key))
        for key in ("edit_render_status", "edited_output_url", "edited_video_duration", "output_validation", "subtitles")
    }
    previous_narration = voiceover.get("narration")
    previous_regenerated_index = voiceover.get("last_regenerated_scene_index")
    previous_regenerated_at = voiceover.get("last_regenerated_at")
    # Keep the scene's authored speech in sync with the replacement. The final
    # edit renderer derives subtitle cues from scene fields, not voiceover.clips.
    previous_scene_lists = {}
    for scene_key in ("_source_scenes", "_edited_scenes"):
        scene_list = record.get(scene_key)
        if isinstance(scene_list, list):
            previous_scene_lists[scene_key] = [
                dict(scene) if isinstance(scene, dict) else scene for scene in scene_list
            ]
            for position, scene in enumerate(scene_list):
                if not isinstance(scene, dict):
                    continue
                source_index = _safe_record_index(scene.get("_source_scene_index"), position)
                if source_index == scene_index:
                    scene["voiceover_text"] = req.text
    clip.update({
        "text": req.text,
        "audio_path": str(generated_path),
        "tts_engine": result.get("engine"),
        "audio_duration": duration,
        "error": None,
        "failure_info": None,
    })
    voiceover["narration"] = " ".join(
        str(item.get("text") or "").strip()
        for item in sorted(clips, key=lambda item: _safe_record_index(item.get("index"), 0))
        if isinstance(item, dict) and str(item.get("text") or "").strip()
    )
    voiceover["last_regenerated_scene_index"] = scene_index
    voiceover["last_regenerated_at"] = time.time()
    record["edit_render_status"] = "stale"
    record["edited_output_url"] = None
    record["edited_video_duration"] = None
    record["output_validation"] = None
    record["subtitles"] = {**(record.get("subtitles") or {}), "status": "stale_after_narration_edit"}
    try:
        _persist_job(record)
    except Exception as exc:  # noqa: BLE001
        clip.clear()
        clip.update(previous_clip)
        if previous_narration is None:
            voiceover.pop("narration", None)
        else:
            voiceover["narration"] = previous_narration
        for scene_key, scene_list in previous_scene_lists.items():
            record[scene_key] = scene_list
        for key, value in (("last_regenerated_scene_index", previous_regenerated_index),
                           ("last_regenerated_at", previous_regenerated_at)):
            if value is None:
                voiceover.pop(key, None)
            else:
                voiceover[key] = value
        for key, (existed, value) in previous_fields.items():
            if existed:
                record[key] = value
            else:
                record.pop(key, None)
        raise HTTPException(status_code=503, detail="Could not persist regenerated narration; previous narration remains active") from exc

    return {
        "job_id": job_id,
        "scene_index": scene_index,
        "status": "narration_replaced",
        "audio_url": f"/videos/jobs/{job_id}/scene-narration/{scene_index}/audio",
        "audio_duration": duration,
        "tts_engine": result.get("engine"),
        "previous_asset_preserved": bool(previous_path),
        "scene_clip_rebuild_required": bool(record.get("vidgrid_compatible")),
        "full_mp4_render_required": True,
        "message": "Somente a fala desta cena foi regenerada. O clipe de 10 segundos precisa ser reconstruído e o MP4 completo reexportado; as demais cenas e arquivos foram preservados.",
    }


@router.post("/jobs/{job_id}/visual-analysis")
async def analyze_video_job_visuals(job_id: str):
    """Score the saved storyboard using studio-specific scene metadata."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    scenes = record.get("_edited_scenes") or record.get("_source_scenes") or []
    if not scenes:
        raise HTTPException(status_code=409, detail="O trabalho ainda não possui cenas para análise visual")
    params = record.get("params") or {}
    studio_id = str(params.get("studio_id") or record.get("studio_id") or "custom")
    fps = int(params.get("frame_rate") or record.get("frame_rate") or 24)
    from modules.ai_video_studio.media.visual_intelligence import analyze_visual_quality
    try:
        report = analyze_visual_quality(scenes, studio_id=studio_id, fps=fps)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    result = {"job_id": job_id, **report}
    record["visual_intelligence"] = result
    _persist_job(record)
    return result




@router.post("/jobs/{job_id}/image-similarity-analysis")
async def analyze_video_job_image_similarity(job_id: str, max_hamming_distance: int = 6):
    """Compare active scene image pixels to find exact and perceptual duplicates."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if not 0 <= max_hamming_distance <= 16:
        raise HTTPException(status_code=422, detail="max_hamming_distance must be between 0 and 16")
    scenes = record.get("_edited_scenes") or record.get("_source_scenes") or []
    if not scenes:
        raise HTTPException(status_code=409, detail="O trabalho ainda não possui cenas para análise")
    from modules.ai_video_studio.media.output_paths import get_subsystem_dir
    image_root = Path(get_subsystem_dir("images")).resolve()
    images: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for index, scene in enumerate(scenes):
        scene_index = int(scene.get("_source_scene_index", index))
        raw_path = scene.get("background_image_path")
        if not raw_path:
            continue
        image_path = Path(str(raw_path)).resolve()
        if image_root not in image_path.parents:
            rejected.append({"scene_index": scene_index, "reason": "image_path_outside_asset_directory"})
            continue
        images.append({"scene_index": scene_index, "path": str(image_path)})
    try:
        from modules.ai_video_studio.media.image_similarity import analyze_scene_image_similarity
        report = await asyncio.to_thread(
            analyze_scene_image_similarity, images,
            max_hamming_distance=max_hamming_distance,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    report["skipped_images"].extend(rejected)
    result = {"job_id": job_id, **report}
    record["image_similarity_analysis"] = result
    _persist_job(record)
    return result

@router.post("/jobs/{job_id}/mp4-visual-analysis")
async def analyze_video_job_mp4_visuals(job_id: str, max_frames: int = 48):
    """Inspect sampled frames from the actual encoded MP4, not storyboard metadata."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    video_path = record.get("edited_output_path") or record.get("output_path")
    if not video_path:
        raise HTTPException(status_code=409, detail="O trabalho ainda não possui um MP4 renderizado")
    if record.get("status") != "completed":
        raise HTTPException(status_code=409, detail="A análise exige um vídeo concluído")
    try:
        from modules.ai_video_studio.media.mp4_visual_analysis import analyze_mp4_visuals
        report = await asyncio.to_thread(
            analyze_mp4_visuals,
            video_path,
            timeline=record.get("edit_timeline"),
            max_frames=max_frames,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    result = {"job_id": job_id, "video_source": "edited" if record.get("edited_output_path") else "original", **report}
    record["mp4_visual_analysis"] = result
    _persist_job(record)
    return result


@router.post("/jobs/{job_id}/av-sync-analysis")
async def analyze_video_job_av_sync(job_id: str):
    """Compare narration clip timing against scene timing in the saved edit timeline."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    timeline = record.get("edit_timeline") or {}
    tracks = timeline.get("tracks") or []
    video_track = next((track for track in tracks if track.get("type") == "video"), None)
    narration_track = next((track for track in tracks if track.get("role") == "narration"), None)
    if not video_track:
        raise HTTPException(status_code=409, detail="Salve uma timeline de vídeo antes de analisar a sincronização")
    params = record.get("params") or {}
    fps = int(timeline.get("fps") or params.get("frame_rate") or record.get("frame_rate") or 24)
    from modules.ai_video_studio.media.av_sync import analyze_av_sync
    try:
        report = analyze_av_sync(
            video_track.get("clips") or [],
            narration_track.get("clips") or [] if narration_track else [],
            fps=fps,
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not narration_track:
        report["status"] = "no_narration"
        report["warnings"].append({
            "code": "narration_track_missing",
            "severity": "info",
            "message": "A timeline não contém faixa de narração por cena.",
        })
    result = {"job_id": job_id, **report}
    record["av_sync_analysis"] = result
    _persist_job(record)
    return result


@router.post("/jobs/{job_id}/audio-analysis")
async def analyze_video_job_audio(job_id: str):
    """Inspect current narration/music/SFX sources and recommend safe mix corrections."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    from modules.ai_video_studio.media.audio_timeline import (
        analyze_audio_file, recommend_ducking, validate_audio_asset,
    )

    configured = record.get("_audio_clips") or {}
    sources: list[tuple[str, str, Path]] = []
    skipped: list[dict[str, str]] = []
    for role, clips in (
        ("music", configured.get("music", [])),
        ("sound_effect", configured.get("sfx", [])),
    ):
        for index, clip in enumerate(clips):
            try:
                asset = validate_audio_asset(clip.get("asset"))
                sources.append((role, f"{role}_{index}", asset))
            except (TypeError, ValueError) as exc:
                skipped.append({"role": role, "reason": str(exc)})

    voiceover = record.get("voiceover")
    voiceover = voiceover if isinstance(voiceover, dict) else {}
    narration_clips = voiceover.get("clips", []) if isinstance(voiceover, dict) else []
    for index, clip in enumerate(narration_clips if isinstance(narration_clips, list) else []):
        if not isinstance(clip, dict) or not clip.get("audio_path"):
            continue
        try:
            asset = validate_audio_asset(clip["audio_path"])
            sources.append(("narration", f"narration_{index}", asset))
        except (TypeError, ValueError) as exc:
            skipped.append({"role": "narration", "reason": str(exc)})

    reports: dict[str, list[dict]] = {"narration": [], "music": [], "sound_effect": []}
    for role, label, asset in sources:
        try:
            report = await asyncio.to_thread(analyze_audio_file, asset)
            report["source"] = label
            reports[role].append(report)
        except (OSError, RuntimeError, ValueError) as exc:
            skipped.append({"role": role, "source": label, "reason": str(exc)})

    warnings = []
    for role, items in reports.items():
        for item in items:
            for warning in item["warnings"]:
                warnings.append({"role": role, "source": item["source"], "code": warning})
    recommendation = recommend_ducking(reports["narration"], reports["music"])
    result = {
        "job_id": job_id,
        "sources_analyzed": sum(len(items) for items in reports.values()),
        "reports": reports,
        "warnings": warnings,
        "skipped": skipped,
        "ducking_recommendation": recommendation,
        "message": "Análise concluída. As recomendações não alteram a mixagem até serem salvas no editor.",
    }
    record["audio_analysis"] = result
    _persist_job(record)
    return result


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
            validated_asset = validate_audio_asset(clip["asset"])
            clip["asset_fingerprint"] = _asset_sha256(validated_asset)
        if any(clip["loop"] for clip in effects):
            raise ValueError("loop is supported for background music only")
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
    record["_audio_settings"] = req.model_dump(exclude={"music_clips", "sfx_clips"})
    record["audio_settings"] = record["_audio_settings"]
    record["edit_timeline"] = timeline
    record["audio_draft_status"] = "saved"
    record["edit_render_quality"] = None
    _persist_job(record)
    return {"job_id": job_id, "edit_timeline": timeline, "audio_draft_status": "saved", "message": "Faixas de música e efeitos salvas. Renderize para aplicar a mixagem ao novo MP4."}

@router.post("/jobs/{job_id}/render-edits")
async def render_video_job_edits(job_id: str):
    """Render the edited storyboard, remap per-scene audio and rebuild subtitles."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    recoverable_failed_vidgrid = (
        record.get("status") == "failed" and bool(record.get("vidgrid_compatible"))
    )
    if (record.get("status") != "completed" and not recoverable_failed_vidgrid) or not record.get("_edited_scenes"):
        raise HTTPException(status_code=409, detail="A completed job or a partially failed VidGrid job with saved scenes is required before final rendering")
    if record.get("_rendering_edits") or record.get("_rebuilding_scene_clips") or record.get("_scene_clip_rebuild_scheduled"):
        raise HTTPException(status_code=409, detail="An edited render is already running")
    if job_id in _scene_batch_jobs:
        raise HTTPException(status_code=409, detail="Wait for scene regeneration to finish before rendering")

    params = record.get("params") or {}
    scenes = record["_edited_scenes"]
    try:
        width, height = _parse_resolution(params.get("resolution") or record.get("resolution") or "1280x720")
        fps = int(params.get("frame_rate") or record.get("frame_rate") or 24)
        if not 1 <= fps <= 120:
            raise ValueError("frame_rate must be between 1 and 120")
        from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
        from modules.ai_video_studio.media.render import (
            concat_vidgrid_scene_clips, render_multi_scene_video, render_mixed_scene_video,
        )
        generated_scene_clips = {
            int(scene.get("_source_scene_index", index)): str(scene["generative_video_path"])
            for index, scene in enumerate(scenes) if scene.get("generative_video_path")
        }
        vidgrid_clip_paths: list[str] = []
        if record.get("vidgrid_compatible"):
            vidgrid_clip_paths = _ordered_vidgrid_clip_paths(record, scenes)
            ordered_indices = [int(scene.get("_source_scene_index", index)) for index, scene in enumerate(scenes)]
            generated_scene_clips = dict(zip(ordered_indices, vidgrid_clip_paths))
        output_path = unique_filename(get_subsystem_dir("videos"), "text_to_video_edited", "mp4")
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    record["_rendering_edits"] = True
    record["edit_render_status"] = "rendering"
    record["edit_render_quality"] = None
    record.pop("edit_render_assembly_fallback", None)
    _persist_job(record)
    try:
        vidgrid_stream_copy_used = False
        if generated_scene_clips:
            # Keep authored transitions: the mixed renderer applies them in FFmpeg
            # and the EDL uses the same crossfade overlap for narration/subtitles.
            from modules.ai_video_studio.media.timeline import build_edit_timeline
            configured_audio = record.get("_audio_clips") or {}
            from modules.ai_video_studio.media.scene_narration import (
                compute_scene_offsets, remap_narration_clips_for_edits, scene_narration_text,
            )
            voiceover_for_timeline = record.get("voiceover") or {}
            original_narration = voiceover_for_timeline.get("clips", []) if isinstance(voiceover_for_timeline, dict) else []
            remapped_narration = (
                remap_narration_clips_for_edits(scenes, original_narration, fps=fps)
                if isinstance(original_narration, list) and voiceover_for_timeline.get("narration_style") == "per_scene"
                else []
            )
            previous = record.get("edit_timeline") or {}
            has_subtitle_track = bool(record.get("subtitles")) or any(
                track.get("type") == "subtitle" for track in previous.get("tracks", [])
            )
            offsets = compute_scene_offsets(scenes, fps=fps)
            subtitle_cues = []
            if has_subtitle_track:
                for index, scene in enumerate(scenes):
                    text_value = scene_narration_text(scene)
                    if text_value:
                        start_seconds = offsets[index]
                        end_seconds = start_seconds + max(1, int(round(float(scene.get("duration") or 3.0) * fps))) / fps
                        subtitle_cues.append({"index": index + 1, "text": text_value, "start": start_seconds, "end": end_seconds})
            mixed_timeline = build_edit_timeline(
                scenes, fps=fps, width=width, height=height,
                narration=remapped_narration, subtitle_cues=subtitle_cues,
                music_clips=configured_audio.get("music", []),
                sfx_clips=configured_audio.get("sfx", []),
            )
            mixed_timeline["tracks"].extend(
                track for track in previous.get("tracks", [])
                if track.get("type") != "video"
                and track.get("role") not in {"narration", "music", "sound_effect"}
                and track.get("type") != "subtitle"
            )
            record["edit_timeline"] = mixed_timeline
            result = None
            if vidgrid_clip_paths:
                from modules.ai_video_studio.media.transitions import transition_spec
                hard_cuts_only = all(transition_spec(scene).get("type") == "cut" for scene in scenes)
                if hard_cuts_only:
                    concat_result = await asyncio.to_thread(
                        concat_vidgrid_scene_clips, vidgrid_clip_paths, output_path,
                        fps=fps, width=width, height=height, expected_scene_duration=10.0,
                    )
                    if concat_result.get("used"):
                        vidgrid_stream_copy_used = True
                        result = {
                            "output_path": concat_result["output_path"],
                            "frames": concat_result["frames"],
                            "bytes": concat_result["bytes"],
                            "engine": concat_result["engine"],
                            "transition_policy": "vidgrid_stream_copy",
                            "transitions_applied": [],
                        }
                        record["edit_render_transition_policy"] = {
                            "mode": "vidgrid_stream_copy",
                            "transitions_applied": [],
                            "message": "Clipes VidGrid compatíveis concatenados sem reencodificar vídeo; áudio será mixado na etapa final.",
                        }
                    else:
                        record["edit_render_assembly_fallback"] = concat_result.get("reason", "incompatible_clips")
            if result is None:
                result = await asyncio.to_thread(
                    render_mixed_scene_video, scenes, output_path, generated_clips=generated_scene_clips,
                    fps=fps, width=width, height=height, require_mp4=True,
                    studio_id=params.get("studio_id") or "custom",
                )
            if not vidgrid_stream_copy_used:
                record["edit_render_transition_policy"] = {
                    "mode": result.get("transition_policy", "frame_accurate"),
                    "transitions_applied": result.get("transitions_applied", []),
                    "message": "Transições aplicadas no render misto; crossfades descontam os mesmos frames na timeline e no áudio/legendas.",
                }
            _persist_job(record)
        else:
            # Procedural-only projects still use the original multi-scene renderer.
            result = await asyncio.to_thread(
                render_multi_scene_video, scenes, output_path,
                fps=fps, width=width, height=height, require_mp4=True,
                studio_id=params.get("studio_id") or "custom",
            )
        rendered_path = result["output_path"]
        audio_status = "silent"
        final_path = rendered_path
        voiceover = record.get("voiceover")
        voiceover = voiceover if isinstance(voiceover, dict) else {}
        narration_clips = voiceover.get("clips") if isinstance(voiceover, dict) else None
        stale_narration_scene_indices = []
        if voiceover.get("narration_style") == "per_scene" and isinstance(narration_clips, list):
            from modules.ai_video_studio.media.scene_narration import (
                narration_text_changes_for_edits, regenerate_changed_scene_narration_async,
            )
            stale_narration_scene_indices = narration_text_changes_for_edits(scenes, narration_clips)
            if stale_narration_scene_indices:
                regenerated = await regenerate_changed_scene_narration_async(
                    scenes, narration_clips, params=params, fps=fps,
                )
                narration_clips = regenerated["clips"]
                voiceover["clips"] = narration_clips
                record["voiceover"] = voiceover
                record["edit_render_narration"] = {
                    "status": "regenerated" if not regenerated["failed_scene_indices"] else "partial",
                    "regenerated_scene_indices": regenerated["regenerated_scene_indices"],
                    "failed_scene_indices": regenerated["failed_scene_indices"],
                }
                _persist_job(record)
        single_track = (
            isinstance(voiceover, dict)
            and voiceover.get("muxed")
            and voiceover.get("narration_style") == "single_track"
        )
        if single_track:
            audio_status = "single_track_not_retimed"

        from modules.ai_video_studio.media.audio import extract_audio_track, mux_audio_into_video
        from modules.ai_video_studio.media.audio_timeline import measure_encoded_audio, mix_audio_timeline
        from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename

        audio_inputs = []
        total_duration = int(round(result["frames"])) / fps
        if single_track:
            # The original single-track voiceover lives inside its source MP4.
            # The edited visual render is silent, so extract and remix the voice.
            source_voiceover_video = voiceover.get("output_path")
            if not source_voiceover_video:
                raise HTTPException(status_code=422, detail="A narração em faixa única não possui arquivo-fonte para a nova mixagem.")
            video_root = Path(get_subsystem_dir("videos")).resolve()
            source_path = Path(source_voiceover_video).resolve()
            if video_root not in source_path.parents or not source_path.is_file():
                raise HTTPException(status_code=422, detail="O arquivo-fonte da narração não está disponível na pasta de vídeos do projeto.")
            narration_wav = unique_filename(get_subsystem_dir("voice"), "edited_single_track_narration", "wav")
            extraction = await asyncio.to_thread(extract_audio_track, source_path, narration_wav)
            if not extraction.get("extracted"):
                raise HTTPException(status_code=422, detail="Não foi possível recuperar a narração original para a mixagem: " + str(extraction.get("reason") or "falha desconhecida"))
            audio_inputs.append({
                "audio_path": extraction.get("output_path") or str(narration_wav),
                "kind": "narration", "start": 0, "end": total_duration, "volume": 1.0,
            })
            audio_status = "single_track_reused_in_mix"

        has_per_scene_narration = isinstance(narration_clips, list) and any(
            isinstance(clip, dict) and clip.get("audio_path") for clip in narration_clips
        )
        if has_per_scene_narration:
            from modules.ai_video_studio.media.scene_narration import (
                build_narration_tracks,
                remap_narration_clips_for_edits,
            )
            remapped_narration = remap_narration_clips_for_edits(scenes, narration_clips, fps=fps)
            audio_inputs.extend({**track, "kind": "narration"} for track in build_narration_tracks(remapped_narration))

        configured_audio = record.get("_audio_clips") or {}
        audio_inputs.extend({**clip, "kind": "music"} for clip in configured_audio.get("music", []))
        audio_inputs.extend({**clip, "kind": "sound_effect"} for clip in configured_audio.get("sfx", []))
        mix_result = None
        final_quality = None
        if audio_inputs:
            audio_path = unique_filename(get_subsystem_dir("mix"), "edited_audio_mix", "wav")
            mix_result = await asyncio.to_thread(
                mix_audio_timeline, audio_inputs, audio_path, total_duration=total_duration,
                **(record.get("_audio_settings") or {}),
            )
            quality_report = mix_result.get("quality") or {}
            final_quality = quality_report
            if quality_report and not quality_report.get("export_allowed", True):
                record["edit_render_quality"] = quality_report
                _persist_job(record)
                raise HTTPException(
                    status_code=422,
                    detail="Exportação bloqueada: o áudio final contém clipping. Reduza os níveis e renderize novamente.",
                )
            muxed_path = unique_filename(get_subsystem_dir("videos"), "text_to_video_edited_final", "mp4")
            mux_result = await asyncio.to_thread(
                mux_audio_into_video, rendered_path, mix_result["output_path"], muxed_path
            )
            if mux_result.get("muxed"):
                final_path = mux_result["output_path"]
                audio_status = "mixed_audio"
                try:
                    encoded_report = await asyncio.to_thread(measure_encoded_audio, final_path)
                    settings = record.get("_audio_settings") or {}
                    target_lufs = float(settings.get("target_lufs", -14.0))
                    target_tp = float(settings.get("true_peak_db", -1.0))
                    measured = encoded_report["measured"]
                    encoded_report.update({
                        "target_lufs": target_lufs if settings.get("loudness_normalization_enabled") else None,
                        "target_true_peak_dbTP": target_tp if settings.get("loudness_normalization_enabled") else None,
                        "loudness_delta_lu": round(measured["integrated_lufs"] - target_lufs, 2) if settings.get("loudness_normalization_enabled") else None,
                        "true_peak_over_target": bool(settings.get("loudness_normalization_enabled") and measured["true_peak_dbTP"] > target_tp + 0.2),
                    })
                    record["edit_render_encoded_audio"] = encoded_report
                    if encoded_report["true_peak_over_target"]:
                        prior_quality = dict(mix_result.get("quality") or {})
                        prior_quality["status"] = "needs_review"
                        prior_quality["export_allowed"] = True
                        prior_quality.setdefault("warnings", []).append({
                            "code": "encoded_aac_true_peak_over_target",
                            "severity": "warning",
                            "message": "O áudio decodificado do MP4 ultrapassou o alvo de true peak; revise a masterização.",
                        })
                        record["edit_render_quality"] = prior_quality
                        final_quality = prior_quality
                except Exception as measure_exc:
                    record["edit_render_encoded_audio"] = {
                        "verified": False, "measurement": "failed", "reason": str(measure_exc)[:300]
                    }
            else:
                # Never mark an export complete when requested audio was not
                # embedded in the deliverable MP4. Keep the diagnostic in the
                # job record; the normal failure path releases the render lock.
                record["edit_render_audio"] = "audio_mux_failed"
                record["edit_render_audio_error"] = str(mux_result.get("error") or "FFmpeg did not mux the audio track")[:300]
                _persist_job(record)
                raise HTTPException(
                    status_code=500,
                    detail="A renderização visual terminou, mas a faixa de áudio não foi incorporada ao MP4. Corrija o áudio e tente exportar novamente.",
                )

        # Rebuild subtitle sidecar against the edited scene order and timing.
        subtitle_status = "not_generated"
        subtitle_info = None
        try:
            from modules.ai_video_studio.media.scene_narration import build_edited_subtitle_scenes
            from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
            from modules.ai_video_studio.services.subtitle_studio import SubtitleStudioService

            subtitle_scenes = build_edited_subtitle_scenes(
                scenes, narration_clips, fps=fps,
                per_scene_narration=(
                    isinstance(voiceover, dict)
                    and voiceover.get("narration_style") == "per_scene"
                ),
            )
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
        record["edit_export_manifest"] = {
            "assembly_mode": (
                "vidgrid_stream_copy" if record.get("edit_render_transition_policy", {}).get("mode") == "vidgrid_stream_copy"
                else "vidgrid_transition_render" if vidgrid_clip_paths
                else "generative_scene_render" if generated_scene_clips
                else "procedural_scene_render"
            ),
            "source_scene_indices": [
                int(scene.get("_source_scene_index", index)) for index, scene in enumerate(scenes)
            ],
            "fallback_reason": record.get("edit_render_assembly_fallback"),
            "video_frames": int(result.get("frames") or 0),
            "target_fps": fps,
            "target_resolution": f"{width}x{height}",
            "audio_status": audio_status,
            "subtitle_status": subtitle_status,
            "stale_narration_scene_indices": stale_narration_scene_indices,
        }
        record.update(
            edited_output_path=final_path,
            edited_output_url=edited_url,
            edited_file_size_bytes=edited_bytes,
            edited_video_duration=edited_duration,
            edit_render_ducking=(mix_result.get("ducking") if isinstance(mix_result, dict) else None),
            edit_render_normalization=(mix_result.get("normalization") if isinstance(mix_result, dict) else None),
            edit_render_loudness=(mix_result.get("loudness") if isinstance(mix_result, dict) else None),
            edit_render_encoded_audio=record.get("edit_render_encoded_audio"),
            edit_render_quality=final_quality,
            edit_render_status="completed",
            edit_render_audio=audio_status,
            edit_render_subtitles=subtitle_status,
            edit_render_stale_narration_scenes=stale_narration_scene_indices,
            edit_render_narration_warning=(
                "A narração antiga foi omitida porque o texto destas cenas mudou; regenere a voz: "
                + ", ".join(str(index + 1) for index in stale_narration_scene_indices)
                if stale_narration_scene_indices else None
            ),
        )
        output_validation = await _persist_output_validation(job_id)
        _persist_job(record)
        return {
            "output_validation": output_validation,
            "job_id": job_id,
            "status": "completed",
            "output_url": edited_url,
            "video_duration": edited_duration,
            "file_size_bytes": edited_bytes,
            "audio_status": audio_status,
            "stale_narration_scene_indices": stale_narration_scene_indices,
            "narration_warning": record.get("edit_render_narration_warning"),
            "encoded_audio_quality": record.get("edit_render_encoded_audio"),
            "subtitle_status": subtitle_status,
            "subtitles": subtitle_info,
            "message": (
                f"MP4 VidGrid montado com {len(vidgrid_clip_paths)} clipes existentes por concatenação sem reencodificação de vídeo."
                if vidgrid_stream_copy_used else
                f"MP4 VidGrid montado com {len(vidgrid_clip_paths)} clipes existentes e renderização das transições."
                if vidgrid_clip_paths else
                f"MP4 misto renderizado com {len(generated_scene_clips)} cena(s) generativa(s) e transições aplicadas."
                if generated_scene_clips else
                "MP4 editado renderizado com as faixas configuradas mixadas."
                if audio_status == "mixed_audio" else
                "MP4 editado renderizado; a narração em faixa única foi preservada na mixagem, sem reposicionamento automático."
                if audio_status == "single_track_reused_in_mix" else
                "MP4 editado renderizado sem faixas de áudio configuradas."
                if audio_status == "silent" else
                "MP4 visual renderizado, mas a muxagem de áudio falhou; consulte o status do áudio."
            ),
            "ducking": (mix_result.get("ducking") if isinstance(mix_result, dict) else None),
            "normalization": (mix_result.get("normalization") if isinstance(mix_result, dict) else None),
            "loudness": (mix_result.get("loudness") if isinstance(mix_result, dict) else None),
            "quality": (mix_result.get("quality") if isinstance(mix_result, dict) else None),
            "mastering": (mix_result.get("mastering") if isinstance(mix_result, dict) else None),
            "generated_scene_count": len(generated_scene_clips),
            "transition_policy": record.get("edit_render_transition_policy") if generated_scene_clips else None,
        }
    except HTTPException:
        quality = record.get("edit_render_quality")
        record["edit_render_status"] = "quality_blocked" if isinstance(quality, dict) and quality.get("export_allowed") is False else "failed"
        _persist_job(record)
        raise
    except Exception as exc:
        record["edit_render_status"] = "failed"
        record["edit_render_error"] = str(exc)[:500]
        _persist_job(record)
        raise HTTPException(status_code=500, detail="Edited video render failed") from exc
    finally:
        # Persist the lock release as well as the render result. Without this
        # final write, the last saved job snapshot can remain stuck at True
        # after a restart even though the in-memory request has finished.
        record["_rendering_edits"] = False
        _persist_job(record)

_dependency_worker_task: asyncio.Task | None = None
_dependency_worker_stop = asyncio.Event()


async def _process_durable_dependency_rebuild(payload: dict) -> None:
    job_id = str(payload.get("job_id") or "")
    changed_asset_ids = list(payload.get("changed_asset_ids") or [])
    record = _jobs.get(job_id)
    if not record or not changed_asset_ids:
        raise RuntimeError("Durable dependency task references a missing job or asset selection")
    execution = record.get("dependency_rebuild_execution")
    if not isinstance(execution, dict):
        raise RuntimeError("Dependency execution record is missing")
    if execution.get("cancel_requested"):
        execution.update({"status": "cancelled", "updated_at": time.time(), "cancelled_at": time.time()})
        _persist_job(record)
        return

    # Recalculate the graph after a lease recovery: completed clips are not rebuilt twice.
    impact = await preview_video_job_dependency_impact(
        job_id, DependencyImpactRequest(changed_asset_ids=changed_asset_ids)
    )
    if impact.get("rebuild_scene_indices"):
        if not record.get("vidgrid_compatible"):
            raise RuntimeError("Affected scene clips require VidGrid selective rebuild")
        recovery = _scene_clip_recovery_plan(record)
        repairable = set(recovery.get("repair_scene_indices") or [])
        pending = sorted(set(impact["rebuild_scene_indices"]) & repairable)
        impact["previously_completed_scene_indices"] = sorted(
            set(impact["rebuild_scene_indices"]) - set(pending)
        )
        impact["rebuild_scene_indices"] = pending
        impact["rebuild_steps"] = [
            step for step in impact.get("rebuild_steps", [])
            if step.get("operation") != "rebuild_scene_clips"
        ]
        if pending:
            impact["rebuild_steps"].insert(0, {
                "operation": "rebuild_scene_clips", "scene_indices": pending,
                "reason": "Worker durável: somente cenas ainda desatualizadas",
            })
    execution["scene_indices"] = list(impact.get("rebuild_scene_indices") or [])
    execution["previously_completed_scene_indices"] = list(
        impact.get("previously_completed_scene_indices") or []
    )
    execution["updated_at"] = time.time()
    _persist_job(record)
    await _run_dependency_rebuild_background(job_id, changed_asset_ids, impact)


async def _process_durable_scene_clip_rebuild(payload: dict) -> None:
    """Run one persisted VidGrid scene-rebuild task idempotently."""
    job_id = str(payload.get("job_id") or "")
    queue_id = str(payload.get("queue_id") or "")
    record = _jobs.get(job_id)
    queue = record.get("scene_clip_rebuild_queue") if record else None
    if not isinstance(queue, dict) or str(queue.get("queue_id") or "") != queue_id:
        raise RuntimeError("Durable scene rebuild task references a missing or replaced queue")
    if queue.get("cancel_requested"):
        queue.update({"status": "cancelled", "current_scene_index": None, "updated_at": time.time()})
        record["scene_clip_rebuild_status"] = "cancelled"
        _persist_job(record)
        return
    recovery = _scene_clip_recovery_plan(record)
    repairable = set(recovery.get("repair_scene_indices") or [])
    requested = set(payload.get("scene_indices") or queue.get("requested_scene_indices") or [])
    pending = sorted(requested & repairable)
    queue["requested_scene_indices"] = pending
    queue["total"] = len(pending)
    queue["status"] = "processing"
    queue["updated_at"] = time.time()
    record["_scene_clip_rebuild_scheduled"] = False
    record["_scene_clip_rebuild_worker"] = True
    _persist_job(record)
    if not pending:
        queue.update({"status": "completed", "completed": 0, "failed": 0,
                      "current_scene_index": None, "results": [], "updated_at": time.time()})
        record["scene_clip_rebuild_status"] = "completed"
        record["_scene_clip_rebuild_worker"] = False
        _persist_job(record)
        return
    try:
        result = await rebuild_stale_video_job_scene_clips(
            job_id, SceneClipRebuildRequest(scene_indices=pending)
        )
        if result.get("failed") and result.get("rebuilt"):
            queue["status"] = "partial"
        if result.get("status") == "failed":
            queue["error"] = "All requested scene clips failed to rebuild"
    finally:
        record["_scene_clip_rebuild_worker"] = False
        record["_scene_clip_rebuild_scheduled"] = False
        _persist_job(record)


async def _dependency_worker_loop(worker_id: str) -> None:
    from modules.ai_video_studio.media.job_store import (
        claim_next_task, complete_task, fail_task, renew_task_lease, list_tasks,
    )

    while not _dependency_worker_stop.is_set():
        task = await asyncio.to_thread(claim_next_task, worker_id, 120)
        if task is None:
            # Surface tasks exhausted by repeated process crashes in the job status.
            failed_tasks = await asyncio.to_thread(list_tasks)
            for failed_task in failed_tasks:
                if failed_task.get("status") != "failed":
                    continue
                payload = failed_task.get("payload") or {}
                record = _jobs.get(str(payload.get("job_id") or ""))
                error = failed_task.get("last_error") or "Worker exhausted its recovery attempts"
                if failed_task.get("task_type") == "dependency_rebuild":
                    execution = record.get("dependency_rebuild_execution") if record else None
                    if isinstance(execution, dict) and execution.get("status") in {"queued", "processing"}:
                        execution.update({"status": "failed", "error": error,
                                          "updated_at": time.time(),
                                          "worker_attempts": failed_task.get("attempts")})
                        _persist_job(record)
                elif failed_task.get("task_type") == "scene_clip_rebuild":
                    queue = record.get("scene_clip_rebuild_queue") if record else None
                    if isinstance(queue, dict) and queue.get("status") in {"queued", "processing", "interrupted"}:
                        queue.update({"status": "failed", "error": error,
                                      "updated_at": time.time(),
                                      "worker_attempts": failed_task.get("attempts"),
                                      "current_scene_index": None})
                        record["scene_clip_rebuild_status"] = "failed"
                        record["_scene_clip_rebuild_scheduled"] = False
                        record["_scene_clip_rebuild_worker"] = False
                        _persist_job(record)
            try:
                await asyncio.wait_for(_dependency_worker_stop.wait(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            break

        task_id = task["task_id"]
        heartbeat_stop = asyncio.Event()

        async def heartbeat() -> None:
            while not heartbeat_stop.is_set():
                try:
                    await asyncio.wait_for(heartbeat_stop.wait(), timeout=20)
                except asyncio.TimeoutError:
                    owned = await asyncio.to_thread(renew_task_lease, task_id, worker_id, 120)
                    if not owned:
                        return

        heartbeat_task = asyncio.create_task(heartbeat())
        try:
            payload = task.get("payload") or {}
            if task.get("task_type") == "dependency_rebuild":
                await _process_durable_dependency_rebuild(payload)
                record = _jobs.get(str(payload.get("job_id") or ""))
                execution = record.get("dependency_rebuild_execution") if record else None
                if isinstance(execution, dict) and execution.get("status") == "failed":
                    raise RuntimeError(str(execution.get("error") or "Dependency rebuild failed"))
            elif task.get("task_type") == "scene_clip_rebuild":
                await _process_durable_scene_clip_rebuild(payload)
            else:
                raise RuntimeError(f"Unsupported durable task type: {task.get('task_type')}")
            await asyncio.to_thread(complete_task, task_id, worker_id)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            retried = await asyncio.to_thread(
                fail_task, task_id, worker_id, str(exc), 15, 3
            )
            payload = task.get("payload") or {}
            record = _jobs.get(str(payload.get("job_id") or ""))
            if task.get("task_type") == "dependency_rebuild":
                execution = record.get("dependency_rebuild_execution") if record else None
                if isinstance(execution, dict):
                    execution.update({
                        "status": "queued" if retried else "failed",
                        "error": str(exc)[:500],
                        "updated_at": time.time(),
                        "worker_attempts": task.get("attempts"),
                        "retry_scheduled": bool(retried),
                    })
                    _persist_job(record)
            elif task.get("task_type") == "scene_clip_rebuild":
                queue = record.get("scene_clip_rebuild_queue") if record else None
                if isinstance(queue, dict):
                    queue.update({
                        "status": "queued" if retried else "failed",
                        "error": str(exc)[:500],
                        "updated_at": time.time(),
                        "worker_attempts": task.get("attempts"),
                        "retry_scheduled": bool(retried),
                        "current_scene_index": None,
                    })
                    record["scene_clip_rebuild_status"] = queue["status"]
                    record["_scene_clip_rebuild_scheduled"] = False
                    record["_scene_clip_rebuild_worker"] = False
                    _persist_job(record)
        finally:
            heartbeat_stop.set()
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass


def start_dependency_rebuild_worker() -> None:
    global _dependency_worker_task
    if _dependency_worker_task is None or _dependency_worker_task.done():
        _dependency_worker_stop.clear()
        _dependency_worker_task = asyncio.create_task(
            _dependency_worker_loop(f"darkstudio-{uuid.uuid4()}")
        )


async def stop_dependency_rebuild_worker() -> None:
    global _dependency_worker_task
    _dependency_worker_stop.set()
    if _dependency_worker_task is not None:
        try:
            await asyncio.wait_for(_dependency_worker_task, timeout=5)
        except asyncio.TimeoutError:
            _dependency_worker_task.cancel()
            try:
                await _dependency_worker_task
            except asyncio.CancelledError:
                pass
        _dependency_worker_task = None


async def _run_dependency_rebuild_background(job_id: str, changed_asset_ids: list[str], impact: dict) -> None:
    """Run a confirmed dependency rebuild outside the request/response cycle."""
    record = _jobs.get(job_id)
    if record is None:
        return
    execution = record.get("dependency_rebuild_execution")
    if not isinstance(execution, dict):
        return
    execution.update({"status": "processing", "started_at": execution.get("queued_at") or time.time(),
                      "updated_at": time.time()})
    _persist_job(record)
    rebuild_result = None
    try:
        if execution.get("cancel_requested"):
            execution.update({"status": "cancelled", "updated_at": time.time(), "cancelled_at": time.time()})
            return
        scene_indices = list(impact.get("rebuild_scene_indices") or [])
        if scene_indices:
            if not record.get("vidgrid_compatible"):
                raise HTTPException(status_code=409, detail="Affected scene clips require VidGrid selective rebuild; regenerate the storyboard clips first.")
            rebuild_result = await rebuild_stale_video_job_scene_clips(
                job_id, SceneClipRebuildRequest(scene_indices=scene_indices)
            )
            if execution.get("cancel_requested"):
                execution.update({"status": "cancelled", "updated_at": time.time(),
                                  "cancelled_at": time.time(), "rebuild_result": rebuild_result,
                                  "final_export_skipped": True})
                return
            if rebuild_result.get("failed") or rebuild_result.get("rebuilt") != len(scene_indices):
                execution.update({"status": "partial", "updated_at": time.time(),
                                  "rebuild_result": rebuild_result, "rebuild": rebuild_result, "render": None, "final_export_skipped": True})
                _persist_job(record)
                return
        if execution.get("cancel_requested"):
            execution.update({"status": "cancelled", "updated_at": time.time(),
                              "cancelled_at": time.time(), "rebuild_result": rebuild_result,
                              "final_export_skipped": True})
            return
        render_result = await render_video_job_edits(job_id)
        execution.update({"status": "completed", "updated_at": time.time(),
                          "rebuild_result": rebuild_result,
                          "render_output_url": render_result.get("output_url"), "render_result": render_result, "render": render_result, "rebuild": rebuild_result})
    except HTTPException as exc:
        execution.update({"status": "failed", "updated_at": time.time(), "error": str(exc.detail)[:500]})
    except Exception as exc:  # noqa: BLE001
        execution.update({"status": "failed", "updated_at": time.time(), "error": str(exc)[:500]})
    finally:
        _persist_job(record)


@router.post("/jobs/{job_id}/dependency-rebuild/resume", status_code=202)
async def resume_video_job_dependency_rebuild(job_id: str, background_tasks: BackgroundTasks):
    """Resume an incomplete dependency rebuild from the current asset state."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    previous = record.get("dependency_rebuild_execution")
    resumable = {"interrupted", "cancelled", "partial", "failed"}
    if not isinstance(previous, dict) or previous.get("status") not in resumable:
        raise HTTPException(status_code=409, detail="Only interrupted, cancelled or incomplete dependency rebuilds can be resumed")
    if record.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Only completed jobs can resume dependency rebuilds")
    if record.get("_rendering_edits") or record.get("_rebuilding_scene_clips") or record.get("_scene_clip_rebuild_scheduled") or job_id in _scene_batch_jobs:
        raise HTTPException(status_code=409, detail="Job assets are locked by another operation")

    changed_asset_ids = list(previous.get("changed_asset_ids") or [])
    if not changed_asset_ids:
        raise HTTPException(status_code=409, detail="The previous execution has no saved asset selection")
    impact = await preview_video_job_dependency_impact(
        job_id, DependencyImpactRequest(changed_asset_ids=changed_asset_ids)
    )
    if not impact.get("final_export_required"):
        return {"job_id": job_id, "status": "unchanged", "queued": False,
                "message": "No downstream export work remains."}

    if impact.get("rebuild_scene_indices"):
        if not record.get("vidgrid_compatible"):
            raise HTTPException(status_code=409, detail="Affected scene clips require VidGrid selective rebuild")
        recovery = _scene_clip_recovery_plan(record)
        repairable = set(recovery.get("repair_scene_indices") or [])
        pending = sorted(set(impact["rebuild_scene_indices"]) & repairable)
        impact["previously_completed_scene_indices"] = sorted(
            set(impact["rebuild_scene_indices"]) - set(pending)
        )
        impact["rebuild_scene_indices"] = pending
        impact["rebuild_steps"] = [
            step for step in impact.get("rebuild_steps", [])
            if step.get("operation") != "rebuild_scene_clips"
        ]
        if pending:
            impact["rebuild_steps"].insert(0, {
                "operation": "rebuild_scene_clips", "scene_indices": pending,
                "reason": "Retomada: somente cenas que continuam desatualizadas",
            })

    graph = await get_video_job_dependency_graph(job_id)
    nodes_by_id = {node["id"]: node for node in graph["nodes"]}
    blocked = [
        {"id": node["id"], "status": node["status"], "reason": node.get("reason")}
        for node in [*impact.get("affected_nodes", []),
                     *(nodes_by_id[node_id] for node_id in changed_asset_ids if node_id in nodes_by_id)]
        if node.get("type") in {"image", "narration", "narration_track", "music", "sound_effect"}
        and node.get("status") in {"missing", "corrupt", "unreadable"}
    ]
    if blocked:
        raise HTTPException(status_code=409, detail={
            "message": "Resume blocked because required assets are unavailable or corrupt",
            "blocked_assets": blocked,
        })

    execution = {
        "status": "queued", "changed_asset_ids": changed_asset_ids,
        "scene_indices": list(impact.get("rebuild_scene_indices") or []),
        "previously_completed_scene_indices": list(impact.get("previously_completed_scene_indices") or []),
        "queued_at": time.time(), "updated_at": time.time(),
        "final_export_required": True, "resume_of": previous.get("queued_at"),
        "cancel_requested": False, "attempt": int(previous.get("attempt") or 1) + 1,
    }
    record["dependency_rebuild_execution"] = execution
    _persist_job(record)
    task_id = str(uuid.uuid4())
    try:
        from modules.ai_video_studio.media.job_store import enqueue_task
        enqueue_task(task_id, "dependency_rebuild", {
            "job_id": job_id, "changed_asset_ids": changed_asset_ids,
        })
    except Exception as exc:
        execution.update({"status": previous.get("status", "interrupted"),
                          "error": f"Não foi possível persistir a retomada: {str(exc)[:400]}",
                          "updated_at": time.time()})
        _persist_job(record)
        raise HTTPException(status_code=503, detail="Durable task queue is unavailable") from exc
    execution["task_id"] = task_id
    _persist_job(record)
    return {
        "job_id": job_id, "status": "queued", "queued": True, "task_id": task_id,
        "scene_indices": execution["scene_indices"],
        "previously_completed_scene_indices": execution["previously_completed_scene_indices"],
        "status_url": f"/videos/jobs/{job_id}/dependency-rebuild/status",
        "message": "Execução gravada na fila persistente; somente cenas ainda desatualizadas serão reconstruídas.",
    }


@router.post("/jobs/{job_id}/execute-dependency-rebuild", status_code=202)
async def execute_video_job_dependency_rebuild(
    job_id: str, req: DependencyExecutionRequest, background_tasks: BackgroundTasks = None
):
    """Queue a freshly recalculated dependency plan after explicit user confirmation."""
    if not req.confirmed:
        raise HTTPException(status_code=409, detail="Explicit confirmation is required before rebuilding assets")
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if record.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Only completed jobs can run dependency rebuilds")
    if record.get("_rendering_edits") or record.get("_rebuilding_scene_clips") or record.get("_scene_clip_rebuild_scheduled") or job_id in _scene_batch_jobs:
        raise HTTPException(status_code=409, detail="Job assets are locked by another operation")
    previous_execution = record.get("dependency_rebuild_execution")
    if isinstance(previous_execution, dict) and previous_execution.get("status") in {"queued", "processing"}:
        raise HTTPException(status_code=409, detail="A dependency rebuild is already in progress")

    impact = await preview_video_job_dependency_impact(
        job_id, DependencyImpactRequest(changed_asset_ids=req.changed_asset_ids)
    )
    if not impact["final_export_required"]:
        return {"job_id": job_id, "status": "unchanged", "queued": False,
                "message": "Os ativos selecionados não exigem reconstrução nem nova exportação.", "impact": impact}

    graph = await get_video_job_dependency_graph(job_id)
    nodes_by_id = {node["id"]: node for node in graph["nodes"]}
    blocked = [
        {"id": node["id"], "status": node["status"], "reason": node.get("reason")}
        for node in [*impact["affected_nodes"], *(nodes_by_id[node_id] for node_id in req.changed_asset_ids if node_id in nodes_by_id)]
        if node.get("type") in {"image", "narration", "narration_track", "music", "sound_effect"}
        and node.get("status") in {"missing", "corrupt", "unreadable"}
    ]
    if blocked:
        raise HTTPException(status_code=409, detail={
            "message": "Rebuild blocked because required assets are unavailable or corrupt",
            "blocked_assets": blocked,
        })

    execution = {
        "status": "queued", "changed_asset_ids": list(req.changed_asset_ids),
        "scene_indices": list(impact["rebuild_scene_indices"]),
        "queued_at": time.time(), "updated_at": time.time(),
        "final_export_required": bool(impact["final_export_required"]),
    }
    record["dependency_rebuild_execution"] = execution
    _persist_job(record)
    task_id = str(uuid.uuid4())
    try:
        from modules.ai_video_studio.media.job_store import enqueue_task
        enqueue_task(task_id, "dependency_rebuild", {
            "job_id": job_id, "changed_asset_ids": list(req.changed_asset_ids),
        })
    except Exception as exc:
        execution.update({"status": "failed", "error": f"Não foi possível persistir a tarefa: {str(exc)[:400]}",
                          "updated_at": time.time()})
        _persist_job(record)
        raise HTTPException(status_code=503, detail="Durable task queue is unavailable") from exc
    execution["task_id"] = task_id
    _persist_job(record)
    return {
        "job_id": job_id, "status": "queued", "queued": True, "executed": False,
        "task_id": task_id, "impact": impact,
        "status_url": f"/videos/jobs/{job_id}/dependency-rebuild/status",
        "message": "Reconstrução gravada na fila persistente; o worker processará a tarefa.",
    }


@router.post("/jobs/{job_id}/dependency-rebuild/cancel")
async def cancel_video_job_dependency_rebuild(job_id: str):
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    execution = record.get("dependency_rebuild_execution")
    if not isinstance(execution, dict) or execution.get("status") not in {"queued", "processing"}:
        raise HTTPException(status_code=409, detail="There is no active dependency rebuild to cancel")
    execution["cancel_requested"] = True
    execution["updated_at"] = time.time()
    _persist_job(record)
    return {
        "job_id": job_id, "status": execution.get("status"), "cancel_requested": True,
        "message": "O cancelamento será aplicado antes da próxima etapa segura; uma cena já em renderização será concluída.",
    }


@router.get("/jobs/{job_id}/dependency-rebuild/status")
async def get_video_job_dependency_rebuild_status(job_id: str):
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    execution = record.get("dependency_rebuild_execution")
    if not isinstance(execution, dict):
        raise HTTPException(status_code=404, detail="No dependency rebuild execution exists for this job")
    return {"job_id": job_id, **execution}


@router.post("/jobs/{job_id}/preview")
async def preview_video_job_edits(job_id: str):
    """Render a lightweight visual preview of the saved edit without touching the final MP4."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if record.get("status") != "completed" or not record.get("_edited_scenes"):
        raise HTTPException(status_code=409, detail="Save a valid timeline draft before previewing")
    if record.get("_rendering_edits") or record.get("_rendering_preview"):
        raise HTTPException(status_code=409, detail="Another render is already running")

    params = record.get("params") or {}
    scenes = [dict(scene) for scene in record["_edited_scenes"]]
    try:
        source_width, source_height = _parse_resolution(
            params.get("resolution") or record.get("resolution") or "1280x720"
        )
        scale = min(640 / source_width, 640 / source_height, 1.0)
        width = max(64, int(source_width * scale) // 2 * 2)
        height = max(64, int(source_height * scale) // 2 * 2)
        fps = min(12, int(params.get("frame_rate") or record.get("frame_rate") or 24))
        from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
        from modules.ai_video_studio.media.render import render_multi_scene_video, render_mixed_scene_video
        generated_scene_clips = {
            int(scene.get("_source_scene_index", index)): str(scene["generative_video_path"])
            for index, scene in enumerate(scenes) if scene.get("generative_video_path")
        }
        output_path = unique_filename(get_subsystem_dir("videos"), "text_to_video_preview", "mp4")
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    record["_rendering_preview"] = True
    _persist_job(record)
    try:
        renderer = render_mixed_scene_video if generated_scene_clips else render_multi_scene_video
        kwargs = {
            "fps": fps, "width": width, "height": height, "require_mp4": True,
            "studio_id": params.get("studio_id") or "custom",
        }
        if generated_scene_clips:
            kwargs["generated_clips"] = generated_scene_clips
        result = await asyncio.to_thread(renderer, scenes, output_path, **kwargs)
        preview_url = to_download_url(result["output_path"])
        record.update(
            edit_preview_path=result["output_path"],
            edit_preview_url=preview_url,
            edit_preview_width=width,
            edit_preview_height=height,
            edit_preview_fps=fps,
            edit_preview_duration=round(result["frames"] / fps, 3),
            edit_preview_generated_scene_count=len(generated_scene_clips),
        )
        _persist_job(record)
        return {
            "job_id": job_id, "status": "completed", "preview_url": preview_url,
            "width": width, "height": height, "fps": fps,
            "duration": round(result["frames"] / fps, 3),
            "generated_scene_count": len(generated_scene_clips),
            "message": "Prévia visual em baixa resolução concluída. Áudio e legendas devem ser conferidos na exportação final.",
        }
    except Exception as exc:
        record["edit_preview_error"] = str(exc)[:400]
        _persist_job(record)
        raise HTTPException(status_code=500, detail="Timeline preview render failed") from exc
    finally:
        record["_rendering_preview"] = False
        _persist_job(record)


@router.get("/jobs/{job_id}/visual-direction")
async def get_video_job_visual_direction(job_id: str):
    """Return safe, scene-level visual direction for the interactive scene editor."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if record.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Visual direction is available after generation completes")
    scenes = record.get("_edited_scenes") or record.get("_source_scenes") or []
    assets = {
        int(item.get("scene_index", -1)): item
        for item in (record.get("scene_assets") or [])
        if isinstance(item, dict)
    }
    output = []
    for index, scene in enumerate(scenes):
        source_index = int(scene.get("_source_scene_index", index))
        asset = assets.get(source_index, {})
        image_url = asset.get("image_url")
        if not image_url and scene.get("background_image_path"):
            image_url = to_download_url(scene["background_image_path"])
        output.append({
            "scene_index": source_index,
            "narration": str(scene.get("voiceover_text") or scene.get("narration") or scene.get("dialogue") or ""),
            "storyboard_scene_id": str(scene.get("storyboard_scene_id") or ""),
            "visual_prompt_full": str(scene.get("visual_prompt_full") or ""),
            "negative_prompt": str(scene.get("negative_prompt") or ""),
            "continuity": scene.get("continuity") or {},
            "storyboard_status": str(scene.get("storyboard_status") or "ready"),
            "visual_prompt": str(scene.get("visual_prompt") or ""),
            "visual_prompt_suggestion": str(scene.get("visual_prompt_suggestion") or ""),
            "visual_direction": str(scene.get("visual_direction") or ""),
            "narrative_beat": str(scene.get("narrative_beat") or "development"),
            "shot_type": str(scene.get("shot_type") or "medium"),
            "image_url": image_url,
            "image_status": str(asset.get("status") or ("generated" if image_url else "missing")),
        })
    return {
        "job_id": job_id,
        "studio_id": str((record.get("params") or {}).get("studio_id") or "custom"),
        "scenes": output,
        "scene_count": len(output),
        "storyboard_report": record.get("storyboard_report") or {},
    }


@router.post("/jobs/{job_id}/validate-output")
async def validate_video_job_output(job_id: str):
    """Probe the latest edited/original MP4 and persist a detailed export report."""
    record = _jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if record.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Only completed jobs can have their export validated")

    from modules.ai_video_studio.media.output_paths import get_subsystem_dir

    # Prefer the latest timeline export; the original generation remains a fallback.
    output_value = record.get("edited_output_path") or record.get("output_path")
    if not output_value:
        raise HTTPException(status_code=422, detail="The job has no output MP4 path")
    output_path = Path(str(output_value)).resolve()
    video_root = Path(get_subsystem_dir("videos")).resolve()
    if video_root not in output_path.parents or not output_path.is_file():
        raise HTTPException(status_code=422, detail="The output MP4 is missing or outside the DARKSTUDIO video directory")

    export_manifest = record.get("edit_export_manifest") or {}
    subtitle_info = record.get("edited_subtitles") or record.get("subtitles") or {}
    subtitle_path_value = subtitle_info.get("file_path") if isinstance(subtitle_info, dict) else None
    subtitle_exists = False
    if subtitle_path_value:
        subtitle_path = Path(str(subtitle_path_value)).resolve()
        subtitle_root = Path(get_subsystem_dir("subtitles")).resolve()
        subtitle_exists = subtitle_root in subtitle_path.parents and subtitle_path.is_file()

    report: dict[str, Any] = {
        "job_id": job_id,
        "path_exists": True,
        "file_size_bytes": output_path.stat().st_size,
        "ffprobe_available": bool(shutil.which("ffprobe")),
        "valid": False,
        "integrity": "not_checked",
        "assembly_mode": export_manifest.get("assembly_mode") or (
            "original_generation" if not record.get("edited_output_path") else "unknown"
        ),
        "source_scene_indices": export_manifest.get("source_scene_indices", []),
        "fallback_reason": export_manifest.get("fallback_reason"),
        "subtitle_status": record.get("edit_render_subtitles") or ("available" if subtitle_exists else "not_generated"),
        "subtitle_file_exists": subtitle_exists,
        "errors": [],
        "warnings": [],
    }
    if report["file_size_bytes"] <= 0:
        report["errors"].append("O arquivo MP4 está vazio.")
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        report["warnings"].append("FFprobe não está instalado; não foi possível validar streams e duração.")
    elif report["file_size_bytes"] > 0:
        try:
            completed = await asyncio.to_thread(
                subprocess.run,
                [ffprobe, "-v", "error", "-show_entries",
                 "format=duration,format_name:stream=index,codec_type,codec_name,profile,width,height,r_frame_rate,avg_frame_rate,pix_fmt,duration,sample_rate,channels",
                 "-of", "json", str(output_path)],
                capture_output=True, text=True, timeout=30, check=False,
            )
            if completed.returncode != 0:
                report["errors"].append((completed.stderr or "FFprobe rejeitou o arquivo.")[:500])
            else:
                metadata = json.loads(completed.stdout or "{}")
                streams = metadata.get("streams") or []
                video_streams = [stream for stream in streams if stream.get("codec_type") == "video"]
                audio_streams = [stream for stream in streams if stream.get("codec_type") == "audio"]
                format_info = metadata.get("format") or {}
                duration = float(format_info.get("duration") or 0)
                report.update(
                    duration_seconds=duration,
                    format_name=format_info.get("format_name"),
                    video_streams=len(video_streams),
                    audio_streams=len(audio_streams),
                    video=video_streams[0] if video_streams else None,
                    audio=audio_streams[0] if audio_streams else None,
                )
                if not video_streams:
                    report["errors"].append("O arquivo não contém stream de vídeo.")
                if duration <= 0:
                    report["errors"].append("A duração do MP4 não pôde ser determinada.")
                if video_streams:
                    video = video_streams[0]
                    report["resolution"] = f"{video.get('width', 0)}x{video.get('height', 0)}"
                    report["fps"] = video.get("avg_frame_rate") or video.get("r_frame_rate")
                    report["video_codec"] = video.get("codec_name")
                    report["pixel_format"] = video.get("pix_fmt")
                    params = record.get("params") if isinstance(record.get("params"), dict) else {}
                    expected_resolution = params.get("resolution") or record.get("resolution")
                    if expected_resolution:
                        try:
                            expected_width, expected_height = _parse_resolution(str(expected_resolution))
                            actual_width = int(video.get("width") or 0)
                            actual_height = int(video.get("height") or 0)
                            if (actual_width, actual_height) != (expected_width, expected_height):
                                report["errors"].append(
                                    f"Resolução final {actual_width}x{actual_height} difere da solicitada "
                                    f"{expected_width}x{expected_height}."
                                )
                        except (TypeError, ValueError):
                            report["warnings"].append("Não foi possível comparar a resolução final com os parâmetros do projeto.")
                    expected_fps = params.get("frame_rate") or record.get("frame_rate") or export_manifest.get("target_fps")
                    actual_rate = video.get("avg_frame_rate") or video.get("r_frame_rate")
                    if expected_fps and actual_rate:
                        try:
                            numerator, denominator = (float(value) for value in str(actual_rate).split("/", 1))
                            measured_fps = numerator / denominator
                            if denominator <= 0 or abs(measured_fps - float(expected_fps)) > max(0.1, float(expected_fps) * 0.01):
                                report["errors"].append(
                                    f"FPS final {measured_fps:.3f} difere do solicitado {float(expected_fps):.3f}."
                                )
                        except (TypeError, ValueError, ZeroDivisionError):
                            report["warnings"].append("Não foi possível comparar o FPS final com os parâmetros do projeto.")
                params = record.get("params") if isinstance(record.get("params"), dict) else {}
                audio_status = str(record.get("edit_render_audio") or "")
                edited_mix_requires_audio = audio_status in {
                    "mixed_audio", "mixed_audio_single_track_omitted",
                }
                audio_expected = (
                    edited_mix_requires_audio
                    or (bool(params.get("voiceover")) and audio_status not in {"silent", "audio_mux_failed"})
                )
                report["audio_expected"] = audio_expected
                if audio_expected and not audio_streams:
                    report["errors"].append("Narração solicitada, mas o MP4 final não contém áudio.")
                elif record.get("edit_render_audio") not in {"silent", "audio_mux_failed"} and not audio_streams:
                    report["warnings"].append("A exportação não contém stream de áudio, embora a etapa de áudio não esteja marcada como silenciosa.")
                if audio_expected and video_streams and audio_streams:
                    try:
                        video_stream_duration = float(video_streams[0].get("duration") or duration)
                    except (TypeError, ValueError):
                        video_stream_duration = duration
                    try:
                        audio_stream_duration = float(audio_streams[0].get("duration") or 0)
                    except (TypeError, ValueError):
                        audio_stream_duration = 0.0
                    report["video_stream_duration_seconds"] = video_stream_duration
                    report["audio_stream_duration_seconds"] = audio_stream_duration or None
                    if audio_stream_duration <= 0:
                        report["warnings"].append(
                            "FFprobe não informou a duração individual da faixa de áudio; a sincronização de duração não pôde ser confirmada."
                        )
                    else:
                        frame_rate = video_streams[0].get("avg_frame_rate") or video_streams[0].get("r_frame_rate") or ""
                        try:
                            numerator, denominator = (int(value) for value in frame_rate.split("/", 1))
                            frame_tolerance = 2 * denominator / numerator if numerator > 0 and denominator > 0 else 0.0
                        except (ValueError, ZeroDivisionError):
                            frame_tolerance = 0.0
                        stream_tolerance = max(0.25, frame_tolerance)
                        delta = audio_stream_duration - video_stream_duration
                        report["audio_video_duration_delta_seconds"] = round(delta, 3)
                        report["audio_video_duration_tolerance_seconds"] = round(stream_tolerance, 3)
                        if delta < -stream_tolerance:
                            report["errors"].append(
                                f"A faixa de áudio termina {abs(delta):.2f}s antes do vídeo; o MP4 final está incompleto."
                            )
                        elif delta > stream_tolerance:
                            report["warnings"].append(
                                f"A faixa de áudio ultrapassa o vídeo em {delta:.2f}s."
                            )
                if record.get("edit_render_audio") == "audio_mux_failed":
                    report["warnings"].append("A mixagem de áudio não foi incorporada ao MP4.")
                if record.get("edit_render_audio") == "single_track_not_retimed":
                    report["warnings"].append("A faixa única original não foi reposicionada automaticamente na timeline.")
                # The final edited timeline may contain a subset or a
                # reordered selection of VidGrid clips. Prefer its measured
                # render duration; the full source clip count is only a
                # fallback for jobs without an edited-export duration.
                expected_duration = float(
                    record.get("edited_video_duration")
                    or (
                        float(record.get("clip_duration_seconds") or 10.0) * len(record.get("scene_clips") or [])
                        if record.get("vidgrid_compatible") and record.get("scene_clips")
                        else record.get("video_duration") or 0
                    )
                )
                if expected_duration > 0 and duration > 0:
                    tolerance = max(1.0, expected_duration * 0.03)
                    report["expected_duration_seconds"] = expected_duration
                    report["duration_tolerance_seconds"] = tolerance
                    if abs(duration - expected_duration) > tolerance:
                        report["warnings"].append(
                            f"Duração medida ({duration:.2f}s) difere da referência ({expected_duration:.2f}s)."
                        )
                if subtitle_path_value and not subtitle_exists:
                    report["warnings"].append("O arquivo lateral de legendas informado não foi encontrado no diretório de legendas.")
                report["integrity"] = "passed" if video_streams and duration > 0 else "failed"
        except (OSError, subprocess.TimeoutExpired, ValueError, json.JSONDecodeError) as exc:
            report["errors"].append(f"Falha ao inspecionar MP4: {str(exc)[:300]}")
            report["integrity"] = "failed"
    report["valid"] = bool(
        report["path_exists"] and report["file_size_bytes"] > 0
        and report["ffprobe_available"] and not report["errors"]
        and report.get("video_streams", 0) > 0 and report.get("duration_seconds", 0) > 0
    )
    if not report["ffprobe_available"]:
        report["integrity"] = "not_verified"
    record["output_validation"] = report
    _persist_job(record)
    return report


async def _persist_output_validation(job_id: str) -> dict[str, Any]:
    """Run the same FFprobe audit after every successful generation or export."""
    try:
        report = await validate_video_job_output(job_id)
    except Exception as exc:  # noqa: BLE001 — rendering result remains available for diagnosis
        report = {
            "job_id": job_id,
            "valid": False,
            "integrity": "not_verified",
            "ffprobe_available": bool(shutil.which("ffprobe")),
            "errors": [f"Validação automática não concluída: {str(exc)[:300]}"],
            "warnings": [],
        }
        record = _jobs.get(job_id)
        if record is not None:
            record["output_validation"] = report
            _persist_job(record)
    return report


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


def _probe_image_api(base_url: str, timeout: float = 1.5) -> tuple[bool, str | None]:
    """Check that the configured AUTOMATIC1111-compatible API responds."""
    import urllib.error
    import urllib.request

    if not base_url:
        return False, "Endpoint de imagens não configurado."
    try:
        from modules.ai_video_studio.ai_image_generator.providers.local_diffusion import _api_base_url
        validated_base = _api_base_url()
    except ValueError as exc:
        return False, str(exc)
    request = urllib.request.Request(
        f"{validated_base}/sdapi/v1/options",
        headers={"Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status < 200 or response.status >= 300:
                return False, f"API de imagens respondeu HTTP {response.status}."
            payload = json.loads(response.read(65536).decode("utf-8"))
            if not isinstance(payload, dict):
                return False, "API de imagens respondeu em formato inesperado."
        return True, None
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError) as exc:
        reason = getattr(exc, "reason", None) or str(exc)
        return False, f"API de imagens indisponível: {str(reason)[:180]}"


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
