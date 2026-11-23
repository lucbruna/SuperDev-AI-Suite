"""Visual planning and candidate inspection endpoints for DARKSTUDIO jobs."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ConfigDict

from modules.ai_video_studio.api.routes import assets as asset_routes
from modules.ai_video_studio.api.routes import video as video_routes
from modules.ai_video_studio.api.urls import to_download_url
from modules.ai_video_studio.media.visual_asset_director import (
    build_scene_visual_brief,
    rank_visual_candidates,
)

from modules.ai_video_studio.media.character_identity import (
    apply_character_identities,
    audit_character_identity,
    create_character_identity,
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


def _profiles_with_current_approved_references(
    record: dict[str, Any], profiles: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    """Drop approvals whose image asset was deleted, moved, or made unavailable."""
    resolved: dict[str, dict[str, Any]] = {}
    for character_id, raw_profile in profiles.items():
        if not isinstance(raw_profile, dict):
            continue
        profile = dict(raw_profile)
        approved_ids = profile.get("approved_reference_asset_ids")
        approved_ids = approved_ids if isinstance(approved_ids, list) else []
        current_approved: list[str] = []
        reviews = dict(profile.get("reference_asset_reviews") or {})
        for asset_id in approved_ids:
            asset_id = str(asset_id)
            if asset_id not in (profile.get("reference_asset_ids") or []):
                continue
            try:
                _resolve_character_reference_asset(record, asset_id)
            except HTTPException:
                reviews[asset_id] = "missing_asset"
                continue
            current_approved.append(asset_id)
        profile["approved_reference_asset_ids"] = current_approved
        profile["reference_asset_reviews"] = reviews
        profile["review_status"] = (
            "references_approved" if current_approved and len(current_approved) == len(profile.get("reference_asset_ids") or [])
            else "partial_reference_approval" if current_approved
            else "needs_reference_review" if profile.get("reference_asset_ids")
            else "needs_reference"
        )
        resolved[str(character_id)] = profile
    return resolved


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

    profiles = record.get("character_identities")
    if not isinstance(profiles, dict):
        profiles = {}
    profiles = _profiles_with_current_approved_references(record, profiles)

    briefs: list[dict[str, Any]] = []
    for position, scene in enumerate(scenes):
        try:
            identity_scene = apply_character_identities(scene, profiles)
            brief = build_scene_visual_brief(
                identity_scene, scene_index=position, studio_id=studio_id
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        identity_prompts = identity_scene.get("character_identity_prompts") or []
        identity_review = identity_scene.get("character_identity_review") or {}
        if identity_prompts:
            identity_text = "\n\n".join(item["prompt"] for item in identity_prompts)
            brief["visual_core"] = (
                str(brief.get("visual_core") or "").rstrip() + "\n\n" + identity_text
            ).strip()
        brief["character_identity_prompts"] = identity_prompts
        brief["character_identity_review"] = identity_review
        if identity_review.get("requires_human_review"):
            brief["requires_human_review"] = True
            brief["status"] = "needs_identity_review"
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


@router.get("/jobs/{job_id}/image-framing")
async def get_job_scene_image_framing(job_id: str):
    """Return saved framing settings keyed by original scene index."""
    record = _job_or_404(job_id)
    scenes = _source_scenes(record)
    framing: dict[str, dict[str, float]] = {}
    from modules.ai_video_studio.media.scene_image_transform import normalize_scene_image_transform
    for position, scene in enumerate(scenes):
        try:
            scene_index = int(scene.get("_source_scene_index", position))
            framing[str(scene_index)] = normalize_scene_image_transform(
                scene.get("background_image_transform")
            )
        except (TypeError, ValueError):
            # Malformed legacy metadata is ignored; the UI uses neutral defaults.
            continue
    return {"job_id": job_id, "scenes": framing}


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


def _resolve_character_reference_asset(record: dict[str, Any], asset_id: str) -> dict[str, Any]:
    """Resolve an image reference from the real project asset registry."""
    asset = asset_routes._assets.get(asset_id)
    if not isinstance(asset, dict):
        raise HTTPException(status_code=404, detail="Character reference image not found in this project")
    project_id = str(record.get("project_id") or "")
    if not project_id or str(asset.get("project_id") or "") != project_id:
        raise HTTPException(status_code=404, detail="Character reference image not found in this project")
    mime_type = str(asset.get("mime_type") or "").lower()
    if asset.get("asset_type") != "image" or not mime_type.startswith("image/"):
        raise HTTPException(status_code=422, detail="Character references must be image assets")
    raw_path = str(asset.get("file_path") or "").strip()
    if not raw_path:
        raise HTTPException(status_code=422, detail="Character reference image has no stored file")
    path = Path(raw_path).expanduser()
    try:
        if not path.is_file() or path.stat().st_size <= 0:
            raise HTTPException(status_code=422, detail="Character reference image file is missing or empty")
        size = path.stat().st_size
    except OSError as exc:
        raise HTTPException(status_code=422, detail="Character reference image file is unavailable") from exc
    return {
        "asset_id": asset_id,
        "name": str(asset.get("name") or path.name),
        "mime_type": mime_type,
        "file_size_bytes": int(asset.get("file_size_bytes") or size),
    }


class CharacterIdentityRequest(BaseModel):
    """Authored character identity contract; references are asset IDs, not paths."""

    model_config = ConfigDict(extra="forbid")
    name: str = Field(..., min_length=1, max_length=120)
    visual_identity: str = Field(..., min_length=1, max_length=4000)
    reference_asset_ids: list[str] = Field(default_factory=list, max_length=24)
    invariants: list[str] = Field(default_factory=list, max_length=32)
    forbidden_variations: list[str] = Field(default_factory=list, max_length=32)


@router.get("/jobs/{job_id}/character-identities")
async def list_job_character_identities(job_id: str):
    """List identity profiles explicitly registered for a video job."""
    record = _job_or_404(job_id)
    profiles = record.get("character_identities")
    if not isinstance(profiles, dict):
        profiles = {}
    return {"job_id": job_id, "profiles": profiles, "count": len(profiles)}


@router.put("/jobs/{job_id}/character-identities/{character_id}")
async def save_job_character_identity(
    job_id: str,
    character_id: str,
    req: CharacterIdentityRequest,
):
    """Create or replace one character identity contract without starting generation."""
    record = _job_or_404(job_id)
    if record.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Character identities require a completed job")
    if any(record.get(key) for key in (
        "_rendering_edits", "_rebuilding_scene_clips", "_scene_clip_rebuild_scheduled"
    )):
        raise HTTPException(status_code=409, detail="Scene assets are locked by an active operation")
    try:
        profile = create_character_identity(
            character_id,
            name=req.name,
            visual_identity=req.visual_identity,
            reference_asset_ids=req.reference_asset_ids,
            invariants=req.invariants,
            forbidden_variations=req.forbidden_variations,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    reference_metadata = [
        _resolve_character_reference_asset(record, asset_id)
        for asset_id in profile["reference_asset_ids"]
    ]
    profile["approved_reference_asset_ids"] = []
    profile["reference_asset_reviews"] = {
        item["asset_id"]: "pending" for item in reference_metadata
    }
    profile["reference_asset_metadata"] = reference_metadata
    profile["review_status"] = "needs_reference_review" if reference_metadata else "needs_reference"
    updated = dict(record)
    stored_profiles = record.get("character_identities")
    profiles = dict(stored_profiles) if isinstance(stored_profiles, dict) else {}
    profiles[character_id] = profile
    updated["character_identities"] = profiles
    try:
        video_routes._persist_job(updated)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Could not persist character identity") from exc
    record.clear()
    record.update(updated)
    return {
        "job_id": job_id,
        "profile": profile,
        "generation_started": False,
        "pixel_identity_verified": False,
    }


class CharacterReferenceReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["approved", "rejected"]


@router.put("/jobs/{job_id}/character-identities/{character_id}/references/{asset_id}")
async def review_job_character_reference(
    job_id: str,
    character_id: str,
    asset_id: str,
    req: CharacterReferenceReviewRequest,
):
    """Approve or reject one real image asset as a character identity reference."""
    record = _job_or_404(job_id)
    if record.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Character references require a completed job")
    if any(record.get(key) for key in (
        "_rendering_edits", "_rebuilding_scene_clips", "_scene_clip_rebuild_scheduled"
    )):
        raise HTTPException(status_code=409, detail="Scene assets are locked by an active operation")
    profiles = record.get("character_identities")
    profile = profiles.get(character_id) if isinstance(profiles, dict) else None
    if not isinstance(profile, dict):
        raise HTTPException(status_code=404, detail="Character identity profile not found")
    if asset_id not in (profile.get("reference_asset_ids") or []):
        raise HTTPException(status_code=404, detail="Image is not registered as a reference for this character")
    asset_metadata = _resolve_character_reference_asset(record, asset_id)

    updated = dict(record)
    updated_profiles = dict(profiles)
    updated_profile = dict(profile)
    reviews = dict(updated_profile.get("reference_asset_reviews") or {})
    reviews[asset_id] = req.status
    approved = list(updated_profile.get("approved_reference_asset_ids") or [])
    if req.status == "approved" and asset_id not in approved:
        approved.append(asset_id)
    if req.status == "rejected":
        approved = [item for item in approved if item != asset_id]
    updated_profile["reference_asset_reviews"] = reviews
    updated_profile["approved_reference_asset_ids"] = approved
    all_refs = list(updated_profile.get("reference_asset_ids") or [])
    updated_profile["review_status"] = (
        "references_approved" if all_refs and all(reviews.get(item) == "approved" for item in all_refs)
        else "partial_reference_approval" if approved
        else "needs_reference_review"
    )
    updated_profiles[character_id] = updated_profile
    updated["character_identities"] = updated_profiles
    try:
        video_routes._persist_job(updated)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Could not persist character reference review") from exc
    record.clear()
    record.update(updated)
    return {
        "job_id": job_id,
        "character_id": character_id,
        "asset": asset_metadata,
        "status": req.status,
        "approved_reference_asset_ids": approved,
        "review_status": updated_profile["review_status"],
        "pixel_identity_verified": False,
    }


@router.get("/jobs/{job_id}/character-identity-audit")
async def get_job_character_identity_audit(job_id: str):
    """Audit explicit scene assignments against registered character profiles."""
    record = _job_or_404(job_id)
    profiles = record.get("character_identities")
    if not isinstance(profiles, dict):
        profiles = {}
    scenes = _source_scenes(record)
    try:
        report = audit_character_identity(scenes, profiles)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"job_id": job_id, "audit": report}
