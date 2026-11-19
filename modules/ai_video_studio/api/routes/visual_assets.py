"""Visual planning and candidate inspection endpoints for DARKSTUDIO jobs."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ConfigDict

from modules.ai_video_studio.api.routes import video as video_routes
from modules.ai_video_studio.api.urls import to_download_url
from modules.ai_video_studio.media.visual_asset_director import (
    build_scene_visual_brief,
    rank_visual_candidates,
)

router = APIRouter()


class SceneImageFramingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scale: float = Field(default=1.0, ge=1.0, le=3.0, allow_inf_nan=False)
    offset_x: float = Field(default=0.0, ge=-1.0, le=1.0, allow_inf_nan=False)
    offset_y: float = Field(default=0.0, ge=-1.0, le=1.0, allow_inf_nan=False)


class VisualPlanRequest(BaseModel):
    """Preview scene visual briefs or save them as editable job metadata."""

    studio_id: str | None = Field(
        default=None,
        pattern="^(whymentary|historical_documentary|felt_clay)$",
    )
    apply_suggestions: bool = Field(
        default=False,
        description="Persist visual briefs and non-destructive prompt suggestions; never replaces images.",
    )


def _job_or_404(job_id: str) -> dict[str, Any]:
    record = video_routes._jobs.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return record


def _source_scenes(record: dict[str, Any]) -> list[dict[str, Any]]:
    scenes = record.get("_edited_scenes") or record.get("_source_scenes") or []
    if not isinstance(scenes, list):
        raise HTTPException(status_code=422, detail="Job scenes are malformed")
    return [dict(scene) for scene in scenes if isinstance(scene, dict)]


@router.post("/jobs/{job_id}/visual-plan")
async def create_job_visual_plan(job_id: str, req: VisualPlanRequest):
    """Create per-scene visual briefs; optional persistence is non-destructive."""
    record = _job_or_404(job_id)
    if record.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Visual planning requires a completed job")

    studio_id = req.studio_id or str((record.get("params") or {}).get("studio_id") or "whymentary")
    if studio_id not in {"whymentary", "historical_documentary", "felt_clay"}:
        raise HTTPException(status_code=422, detail="Unsupported studio for visual planning")

    if req.apply_suggestions and any(record.get(key) for key in (
        "_rendering_edits", "_rebuilding_scene_clips", "_scene_clip_rebuild_scheduled"
    )):
        raise HTTPException(status_code=409, detail="Scene assets are locked by an active render operation")

    scenes = _source_scenes(record)
    if not scenes:
        raise HTTPException(status_code=422, detail="Job has no usable scenes")

    briefs: list[dict[str, Any]] = []
    for position, scene in enumerate(scenes):
        try:
            brief = build_scene_visual_brief(scene, scene_index=position, studio_id=studio_id)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        source_index = scene.get("_source_scene_index", position)
        try:
            brief["scene_index"] = int(source_index)
        except (TypeError, ValueError):
            brief["scene_index"] = position
        brief["scene_position"] = position
        briefs.append(brief)

    plan = {
        "studio_id": studio_id,
        "created_at": time.time(),
        "scene_count": len(briefs),
        "ready_count": sum(item["status"] == "ready_for_generation" for item in briefs),
        "review_count": sum(item["requires_human_review"] for item in briefs),
        "briefs": briefs,
        "images_replaced": False,
        "generation_started": False,
    }

    if req.apply_suggestions:
        editable_scenes = _source_scenes(record)
        for brief in briefs:
            scene = editable_scenes[brief["scene_position"]]
            scene["visual_brief"] = brief
            current = str(scene.get("visual_prompt") or "").strip()
            if not current or current.casefold() in {"cena", "imagem", "ilustração", "visual"}:
                scene["visual_prompt_suggestion"] = brief["visual_core"]
        record["_edited_scenes"] = editable_scenes
        record["scene_visual_plan"] = plan
        video_routes._persist_job(record)

    return {
        "job_id": job_id,
        "applied": req.apply_suggestions,
        "plan": plan,
        "message": (
            "Briefings salvos no job. Nenhuma imagem foi substituída e nenhuma geração foi iniciada."
            if req.apply_suggestions
            else "Prévia calculada. Nada foi alterado no job."
        ),
    }


@router.get("/jobs/{job_id}/visual-plan")
async def get_job_visual_plan(job_id: str):
    """Return the last persisted visual plan, if one exists."""
    record = _job_or_404(job_id)
    plan = record.get("scene_visual_plan")
    if not isinstance(plan, dict):
        return {"job_id": job_id, "exists": False, "plan": None}
    return {"job_id": job_id, "exists": True, "plan": plan}


@router.get("/jobs/{job_id}/scenes/{scene_index}/image-candidates")
async def list_job_scene_image_candidates(job_id: str, scene_index: int):
    """Return sanitized, metadata-ranked candidates for one scene."""
    record = _job_or_404(job_id)
    if scene_index < 0:
        raise HTTPException(status_code=422, detail="scene_index must be non-negative")

    scenes = _source_scenes(record)
    scene = next(
        (item for position, item in enumerate(scenes)
         if int(item.get("_source_scene_index", position)) == scene_index),
        None,
    )
    if scene is None and scene_index < len(scenes):
        scene = scenes[scene_index]
    if scene is None:
        raise HTTPException(status_code=404, detail="Scene index not found")

    buckets = record.get("scene_image_candidates")
    candidates = buckets.get(str(scene_index), []) if isinstance(buckets, dict) else []
    if not isinstance(candidates, list):
        candidates = []
    ranked = rank_visual_candidates(scene, [item for item in candidates if isinstance(item, dict)])

    sanitized = []
    for candidate in ranked:
        image_url = candidate.get("image_url")
        if not image_url and candidate.get("image_path"):
            try:
                image_url = to_download_url(str(candidate["image_path"]))
            except Exception:
                image_url = None
        sanitized.append({
            "candidate_id": candidate.get("candidate_id"),
            "scene_index": scene_index,
            "image_url": image_url,
            "provider": candidate.get("provider"),
            "operation": candidate.get("operation"),
            "prompt": candidate.get("prompt"),
            "negative_prompt": candidate.get("negative_prompt"),
            "seed": candidate.get("seed"),
            "status": candidate.get("status", "pending_approval"),
            "metadata_match_score": candidate.get("metadata_match_score", 0.0),
            "metadata_match_terms": candidate.get("metadata_match_terms", []),
        })

    return {
        "job_id": job_id,
        "scene_index": scene_index,
        "candidate_count": len(sanitized),
        "candidates": sanitized,
        "ranking_note": "A ordenação usa palavras-chave dos metadados, não análise visual dos pixels.",
    }



@router.get("/jobs/{job_id}/scenes/{scene_index}/image-history")
async def list_job_scene_image_history(job_id: str, scene_index: int):
    """List restorable historical images without exposing local filesystem paths."""
    record = _job_or_404(job_id)
    if scene_index < 0:
        raise HTTPException(status_code=422, detail="scene_index must be non-negative")
    from modules.ai_video_studio.media.output_paths import get_subsystem_dir
    from modules.ai_video_studio.media.scene_visual_asset_workflow import list_scene_image_history
    entries = list_scene_image_history(
        record, scene_index, image_root=Path(get_subsystem_dir("images")).resolve(),
        image_url_builder=to_download_url,
    )
    return {"job_id": job_id, "scene_index": scene_index, "history_count": len(entries), "history": entries}


@router.post("/jobs/{job_id}/scenes/{scene_index}/image-history/{history_id}/restore")
async def restore_job_scene_image_history(job_id: str, scene_index: int, history_id: str):
    """Restore one previous image and invalidate only its dependent scene clip."""
    record = _job_or_404(job_id)
    if scene_index < 0:
        raise HTTPException(status_code=422, detail="scene_index must be non-negative")
    if record.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Image history can only be restored after job completion")
    if job_id in getattr(video_routes, "_scene_batch_jobs", set()) or any(record.get(key) for key in (
        "_rendering_edits", "_rebuilding_scene_clips", "_scene_clip_rebuild_scheduled"
    )):
        raise HTTPException(status_code=409, detail="Scene assets are locked by an active operation")

    from modules.ai_video_studio.media.output_paths import get_subsystem_dir
    from modules.ai_video_studio.media.scene_visual_asset_workflow import (
        list_scene_image_history, restore_scene_image_history,
    )
    image_root = Path(get_subsystem_dir("images")).resolve()
    try:
        updated, restored = restore_scene_image_history(
            record, scene_index, history_id, image_root=image_root, image_url_builder=to_download_url,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Image history entry not found") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        video_routes._persist_job(updated)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Could not persist restored scene image") from exc
    record.clear()
    record.update(updated)
    image_path = str(Path(str(restored["image_path"])).resolve())
    return {
        "job_id": job_id, "scene_index": scene_index, "history_id": history_id,
        "status": "restored", "image_url": to_download_url(image_path), "render_required": True,
        "message": "Imagem anterior restaurada. A versão que estava ativa foi preservada no histórico para permitir desfazer; somente o clipe desta cena ficou desatualizado.",
        "history": list_scene_image_history(
            record, scene_index, image_root=image_root, image_url_builder=to_download_url,
        ),
    }


@router.put("/jobs/{job_id}/scenes/{scene_index}/image-framing")
async def update_job_scene_image_framing(job_id: str, scene_index: int, req: SceneImageFramingRequest):
    """Persist image framing and invalidate only the affected scene clip."""
    record = _job_or_404(job_id)
    if scene_index < 0:
        raise HTTPException(status_code=422, detail="scene_index must be non-negative")
    if record.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Scene framing requires a completed job")
    if job_id in getattr(video_routes, "_scene_batch_jobs", set()) or any(record.get(key) for key in ("_rendering_edits", "_rebuilding_scene_clips", "_scene_clip_rebuild_scheduled")):
        raise HTTPException(status_code=409, detail="Scene assets are locked by an active operation")
    scenes = _source_scenes(record)
    position = next((i for i, scene in enumerate(scenes) if int(scene.get("_source_scene_index", i)) == scene_index), None)
    if position is None and scene_index < len(scenes):
        position = scene_index
    if position is None:
        raise HTTPException(status_code=404, detail="Scene index not found")
    from modules.ai_video_studio.media.scene_image_transform import normalize_scene_image_transform
    try:
        transform = normalize_scene_image_transform(req.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    scenes[position]["background_image_transform"] = transform
    updated = dict(record)
    updated["_edited_scenes"] = scenes
    clips = [dict(item) for item in (record.get("scene_clips") or []) if isinstance(item, dict)]
    matched = False
    for clip in clips:
        try:
            idx = int(clip.get("scene_index", -1))
        except (TypeError, ValueError):
            continue
        if idx == scene_index:
            clip["status"] = "stale"
            clip["reason"] = "O enquadramento foi alterado; reconstrua este clipe VidGrid."
            matched = True
    if matched:
        updated["scene_clips"] = clips
    try:
        video_routes._persist_job(updated)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Could not persist scene framing") from exc
    record.clear()
    record.update(updated)
    return {"job_id": job_id, "scene_index": scene_index, "status": "saved", "background_image_transform": transform, "clip_invalidated": matched, "render_started": False}
