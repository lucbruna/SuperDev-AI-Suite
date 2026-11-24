"""Visual planning and candidate inspection endpoints for DARKSTUDIO jobs."""
from __future__ import annotations

import asyncio
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



class CharacterReferenceEditRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt: str = Field(..., min_length=1, max_length=4000)
    negative_prompt: str = Field(default="", max_length=2000)
    denoising_strength: float = Field(default=0.35, ge=0.05, le=0.95, allow_inf_nan=False)
    steps: int = Field(default=20, ge=1, le=60)
    cfg_scale: float = Field(default=7.0, ge=1.0, le=20.0, allow_inf_nan=False)


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



@router.post("/jobs/{job_id}/character-identities/{character_id}/references/{asset_id}/generate")
async def generate_character_reference_edit(
    job_id: str,
    character_id: str,
    asset_id: str,
    req: CharacterReferenceEditRequest,
):
    """Run AUTOMATIC1111 img2img using one currently approved project reference."""
    record = _job_or_404(job_id)
    if record.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Character reference generation requires a completed job")
    if any(record.get(key) for key in (
        "_rendering_edits", "_rebuilding_scene_clips", "_scene_clip_rebuild_scheduled"
    )):
        raise HTTPException(status_code=409, detail="Scene assets are locked by an active operation")
    profiles = record.get("character_identities")
    profile = profiles.get(character_id) if isinstance(profiles, dict) else None
    if not isinstance(profile, dict):
        raise HTTPException(status_code=404, detail="Character identity profile not found")

    current_profiles = _profiles_with_current_approved_references(
        record, {character_id: profile}
    )
    current_profile = current_profiles.get(character_id) or {}
    if asset_id not in current_profile.get("approved_reference_asset_ids", []):
        raise HTTPException(status_code=409, detail="Character reference must be approved and currently available")

    metadata = _resolve_character_reference_asset(record, asset_id)
    asset = asset_routes._assets.get(asset_id) or {}
    source_path = Path(str(asset.get("file_path") or "")).expanduser()
    max_reference_bytes = 12 * 1024 * 1024
    try:
        if not source_path.is_file():
            raise HTTPException(status_code=422, detail="Character reference image file is unavailable")
        if source_path.stat().st_size > max_reference_bytes:
            raise HTTPException(status_code=413, detail="Character reference image exceeds the 12 MiB limit")
        source_bytes = source_path.read_bytes()
    except HTTPException:
        raise
    except OSError as exc:
        raise HTTPException(status_code=422, detail="Character reference image could not be read") from exc
    if not source_bytes or len(source_bytes) > max_reference_bytes:
        raise HTTPException(status_code=413 if source_bytes else 422, detail="Character reference image is empty or exceeds the 12 MiB limit")

    try:
        from modules.ai_video_studio.ai_image_generator.providers.local_diffusion import edit_image_bytes
        result = await asyncio.to_thread(
            edit_image_bytes,
            source_bytes,
            req.prompt,
            source_mime_type=metadata["mime_type"],
            negative_prompt=req.negative_prompt,
            denoising_strength=req.denoising_strength,
            steps=req.steps,
            cfg_scale=req.cfg_scale,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail="Configured AUTOMATIC1111-compatible image provider failed") from exc

    return {
        "job_id": job_id,
        "character_id": character_id,
        "provider": result.get("provider"),
        "operation": result.get("operation"),
        "status": "reference_transmitted",
        "reference_asset_id": asset_id,
        "reference_transmitted": bool(result.get("reference_transmitted")),
        "reference_bytes": int(result.get("reference_bytes") or 0),
        "output_path": result.get("image_path"),
        "download_url": to_download_url(result["image_path"]),
        "seed": result.get("seed"),
        "pixel_identity_verified": False,
        "message": "A imagem aprovada foi enviada como init_images ao img2img. Isso condiciona a edição, mas não garante identidade visual idêntica.",
    }


@router.get("/jobs/{job_id}/character-identity-audit")
async def get_job_character_identity_audit(job_id: str):
    """Audit explicit scene assignments against registered character profiles."""
    record = _job_or_404(job_id)
    profiles = record.get("character_identities")
    if not isinstance(profiles, dict):
        profiles = {}
    profiles = _profiles_with_current_approved_references(record, profiles)
    scenes = _source_scenes(record)
    try:
        report = audit_character_identity(scenes, profiles)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"job_id": job_id, "audit": report}


class SceneCharacterImageGenerationRequest(BaseModel):
    """Generate one scene image conditioned on its single approved character."""
    model_config = ConfigDict(extra="forbid")
    prompt: str | None = Field(default=None, max_length=4000)
    negative_prompt: str = Field(default="", max_length=2000)
    denoising_strength: float = Field(default=0.32, ge=0.05, le=0.95, allow_inf_nan=False)
    steps: int = Field(default=20, ge=1, le=60)
    cfg_scale: float = Field(default=7.0, ge=1.0, le=20.0, allow_inf_nan=False)


@router.post("/jobs/{job_id}/scenes/{scene_index}/generate-character-image")
async def generate_scene_character_image(
    job_id: str, scene_index: int, req: SceneCharacterImageGenerationRequest
):
    """Generate a pending scene-image candidate using one approved character reference."""
    record = _job_or_404(job_id)
    if record.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Scene image generation requires a completed job")
    if scene_index < 0:
        raise HTTPException(status_code=422, detail="scene_index must be non-negative")
    if job_id in getattr(video_routes, "_scene_batch_jobs", set()) or any(record.get(key) for key in (
        "_rendering_edits", "_rebuilding_scene_clips", "_scene_clip_rebuild_scheduled"
    )):
        raise HTTPException(status_code=409, detail="Scene assets are locked by an active operation")

    scenes = _source_scenes(record)
    position = next(
        (i for i, item in enumerate(scenes)
         if int(item.get("_source_scene_index", i)) == scene_index),
        None,
    )
    if position is None and scene_index < len(scenes):
        position = scene_index
    if position is None:
        raise HTTPException(status_code=404, detail="Scene index not found")
    scene = scenes[position]

    raw_profiles = record.get("character_identities")
    profiles = raw_profiles if isinstance(raw_profiles, dict) else {}
    profiles = _profiles_with_current_approved_references(record, profiles)
    from modules.ai_video_studio.media.scene_visual_asset_workflow import stage_scene_image_candidate
    from modules.ai_video_studio.media.character_identity import build_character_identity_prompt
    from modules.ai_video_studio.media.output_paths import get_subsystem_dir
    from uuid import uuid4

    raw_character_ids = scene.get("character_ids")
    if not isinstance(raw_character_ids, list) or not raw_character_ids:
        raise HTTPException(status_code=409, detail="Scene must explicitly declare character_ids before character-consistent generation")
    character_ids = list(dict.fromkeys(str(value).strip() for value in raw_character_ids if str(value).strip()))
    if not character_ids:
        raise HTTPException(status_code=409, detail="Scene has no valid character IDs")
    selected_profiles: dict[str, dict[str, Any]] = {}
    reference_paths: dict[str, Path] = {}
    reference_metadata: dict[str, dict[str, Any]] = {}
    for character_id in character_ids:
        profile = profiles.get(character_id)
        if not isinstance(profile, dict):
            raise HTTPException(status_code=409, detail=f"Character identity profile '{character_id}' is missing")
        approved = [
            item for item in (profile.get("approved_reference_asset_ids") or [])
            if item in (profile.get("reference_asset_ids") or [])
        ]
        if not approved:
            raise HTTPException(status_code=409, detail=f"Character '{character_id}' has no currently approved reference")
        asset_id = str(approved[0])
        try:
            metadata = _resolve_character_reference_asset(record, asset_id)
        except HTTPException:
            raise
        asset = asset_routes._assets.get(asset_id) or {}
        source_path = Path(str(asset.get("file_path") or "")).expanduser()
        try:
            if not source_path.is_file():
                raise HTTPException(status_code=422, detail=f"Reference image for '{character_id}' is unavailable")
            if source_path.stat().st_size > 12 * 1024 * 1024:
                raise HTTPException(status_code=413, detail=f"Reference image for '{character_id}' exceeds 12 MiB")
            if source_path.stat().st_size <= 0:
                raise HTTPException(status_code=422, detail=f"Reference image for '{character_id}' is empty")
        except OSError as exc:
            raise HTTPException(status_code=422, detail=f"Reference image for '{character_id}' could not be read") from exc
        selected_profiles[character_id] = profile
        reference_paths[character_id] = source_path
        reference_metadata[character_id] = {**metadata, "asset_id": asset_id}

    identity_prompts = [
        build_character_identity_prompt(selected_profiles[character_id])["prompt"]
        for character_id in character_ids
    ]
    visual_brief = scene.get("visual_brief")
    scene_prompt = str(visual_brief.get("visual_core") or "").strip() if isinstance(visual_brief, dict) else ""
    scene_prompt = (
        str(req.prompt or "").strip()
        or scene_prompt
        or str(scene.get("visual_prompt_suggestion") or scene.get("visual_prompt") or scene.get("description") or "").strip()
    )
    if not scene_prompt:
        raise HTTPException(status_code=422, detail="Scene has no visual prompt or description")
    full_prompt = (
        scene_prompt + "\\n\\n" + "\\n\\n".join(identity_prompts)
        + "\\n\\nUse the supplied character reference images as visual identity anchors. "
        "Preserve each character's face, hair, clothing, proportions and felt material style. "
        "Change only pose, expression, camera composition and scene interaction."
    )[:8000]

    image_root = Path(get_subsystem_dir("images")).resolve()
    image_root.mkdir(parents=True, exist_ok=True)
    output_path = image_root / f"scene_{scene_index}_character_{uuid4().hex}.png"
    try:
        from modules.ai_video_studio.ai_image_generator.providers.comfyui_image_provider import ComfyUIImageProvider
        comfy_provider = ComfyUIImageProvider()
        if comfy_provider.is_configured():
            result = await asyncio.to_thread(
                comfy_provider.generate,
                prompt=full_prompt,
                references_by_character=reference_paths,
                output_path=output_path,
                negative_prompt=req.negative_prompt,
            )
            provider_name = result.get("provider", "comfyui_image_workflow")
            reference_transmitted = True
            reference_bytes = sum(path.stat().st_size for path in reference_paths.values())
            operation = "scene_multi_character_comfyui_image"
        elif len(character_ids) > 1:
            raise HTTPException(
                status_code=503,
                detail="Scenes with multiple characters require DARKSTUDIO_COMFYUI_IMAGE_WORKFLOW and DARKSTUDIO_COMFYUI_IMAGE_MAPPING; AUTOMATIC1111 img2img supports only one reference image.",
            )
        else:
            source_path = reference_paths[character_ids[0]]
            source_bytes = source_path.read_bytes()
            metadata = reference_metadata[character_ids[0]]
            from modules.ai_video_studio.ai_image_generator.providers.local_diffusion import edit_image_bytes
            result = await asyncio.to_thread(
                edit_image_bytes, source_bytes, full_prompt,
                source_mime_type=metadata["mime_type"],
                negative_prompt=req.negative_prompt,
                denoising_strength=req.denoising_strength,
                steps=req.steps,
                cfg_scale=req.cfg_scale,
            )
            provider_name = result.get("provider", "automatic1111_compatible")
            reference_transmitted = bool(result.get("reference_transmitted"))
            reference_bytes = int(result.get("reference_bytes") or len(source_bytes))
            operation = "scene_character_image_to_image"
            output_path = Path(str(result.get("image_path") or "")).resolve()
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail="Configured scene image provider failed") from exc
    except TimeoutError as exc:
        raise HTTPException(status_code=504, detail="Scene image provider timed out") from exc

    if image_root not in output_path.resolve().parents or not output_path.is_file() or output_path.stat().st_size <= 0:
        raise HTTPException(status_code=502, detail="Image provider returned an invalid output outside the DARKSTUDIO image directory")

    candidate_id = str(uuid4())
    candidate = {
        "candidate_id": candidate_id,
        "image_path": str(output_path),
        "image_url": to_download_url(str(output_path)),
        "provider": provider_name,
        "operation": operation,
        "prompt": full_prompt,
        "negative_prompt": req.negative_prompt,
        "seed": result.get("seed", -1),
        "status": "pending_approval",
        "character_id": character_ids[0] if len(character_ids) == 1 else None,
        "character_ids": character_ids,
        "reference_asset_id": reference_metadata[character_ids[0]]["asset_id"] if len(character_ids) == 1 else None,
        "reference_asset_ids": [reference_metadata[item]["asset_id"] for item in character_ids],
        "reference_transmitted": reference_transmitted,
        "reference_bytes": reference_bytes,
        "pixel_identity_verified": False,
    }
    try:
        updated = stage_scene_image_candidate(record, scene_index, candidate)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    try:
        video_routes._persist_job(updated)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Could not persist generated scene image candidate") from exc
    record.clear()
    record.update(updated)
    return {
        "job_id": job_id,
        "scene_index": scene_index,
        "candidate_id": candidate_id,
        "status": "pending_approval",
        "image_url": candidate["image_url"],
        "provider": candidate["provider"],
        "character_ids": character_ids,
        "reference_asset_ids": candidate["reference_asset_ids"],
        "reference_transmitted": candidate["reference_transmitted"],
        "pixel_identity_verified": False,
        "active_image_replaced": False,
        "clip_invalidated": False,
        "message": "Imagem gerada como candidata. Aprove-a separadamente para substituir a imagem ativa; a identidade visual ainda exige revisão humana.",
    }
