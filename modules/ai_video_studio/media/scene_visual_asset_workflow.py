"""Safe candidate lifecycle helpers for editable scene images.

The helpers operate on a copied job record and never mutate the caller's object.
They intentionally do not render clips or call image-generation providers.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any
from time import time
from uuid import uuid4


def _candidate_bucket(record: dict[str, Any], scene_index: int) -> list[dict[str, Any]]:
    buckets = record.get("scene_image_candidates")
    if not isinstance(buckets, dict):
        return []
    items = buckets.get(str(scene_index), [])
    return [item for item in items if isinstance(item, dict)] if isinstance(items, list) else []


def _assert_editable(record: dict[str, Any]) -> None:
    if record.get("status") != "completed":
        raise ValueError("Scene image candidates can only be changed after job completion")
    if any(record.get(key) for key in (
        "_rendering_edits", "_rebuilding_scene_clips", "_scene_clip_rebuild_scheduled"
    )):
        raise RuntimeError("Scene assets are locked by an active render operation")


def list_scene_image_candidates(record: dict[str, Any], scene_index: int | None = None) -> list[dict[str, Any]]:
    """Return detached candidate metadata, optionally for one scene."""
    buckets = record.get("scene_image_candidates")
    if not isinstance(buckets, dict):
        return []
    selected = [str(scene_index)] if scene_index is not None else sorted(buckets, key=lambda value: (not value.isdigit(), value))
    result: list[dict[str, Any]] = []
    for key in selected:
        items = buckets.get(key, [])
        if isinstance(items, list):
            result.extend(deepcopy(item) for item in items if isinstance(item, dict))
    return result


def stage_scene_image_candidate(
    record: dict[str, Any], scene_index: int, candidate: dict[str, Any], *, max_per_scene: int = 8
) -> dict[str, Any]:
    """Add a pending candidate without changing the active scene image."""
    _assert_editable(record)
    if isinstance(scene_index, bool) or not isinstance(scene_index, int) or scene_index < 0:
        raise ValueError("scene_index must be a non-negative integer")
    if not isinstance(candidate, dict):
        raise ValueError("candidate must be a dictionary")
    candidate_id = str(candidate.get("candidate_id") or "").strip()
    image_path = str(candidate.get("image_path") or "").strip()
    if not candidate_id or not image_path:
        raise ValueError("candidate_id and image_path are required")
    if max_per_scene < 1:
        raise ValueError("max_per_scene must be positive")

    updated = deepcopy(record)
    bucket = _candidate_bucket(updated, scene_index)
    if any(str(item.get("candidate_id")) == candidate_id for item in bucket):
        raise ValueError("candidate_id already exists for this scene")
    if len(bucket) >= max_per_scene:
        raise ValueError("Maximum pending candidates reached for this scene")
    normalized = {
        **deepcopy(candidate),
        "candidate_id": candidate_id,
        "scene_index": scene_index,
        "status": "pending_approval",
    }
    updated.setdefault("scene_image_candidates", {})[str(scene_index)] = [*bucket, normalized]
    return updated


def discard_scene_image_candidate(
    record: dict[str, Any], scene_index: int, candidate_id: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Remove one candidate while preserving the active scene and its clips."""
    _assert_editable(record)
    updated = deepcopy(record)
    bucket = _candidate_bucket(updated, scene_index)
    selected = next((item for item in bucket if str(item.get("candidate_id")) == candidate_id), None)
    if selected is None:
        raise KeyError("Image candidate not found")
    remaining = [item for item in bucket if str(item.get("candidate_id")) != candidate_id]
    if remaining:
        updated.setdefault("scene_image_candidates", {})[str(scene_index)] = remaining
    else:
        updated.setdefault("scene_image_candidates", {}).pop(str(scene_index), None)
    return updated, deepcopy(selected)


def _find_scene_position(scenes: list[dict[str, Any]], scene_index: int) -> int:
    for position, scene in enumerate(scenes):
        try:
            source_index = int(scene.get("_source_scene_index", position))
        except (TypeError, ValueError):
            source_index = position
        if source_index == scene_index:
            return position
    if 0 <= scene_index < len(scenes):
        return scene_index
    raise KeyError("Scene index not found")


def approve_scene_image_candidate(
    record: dict[str, Any],
    scene_index: int,
    candidate_id: str,
    *,
    image_root: str | Path,
    image_url_builder,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Promote a valid candidate, preserve history, and mark its clip stale."""
    _assert_editable(record)
    updated = deepcopy(record)
    bucket = _candidate_bucket(updated, scene_index)
    candidate = next((item for item in bucket if str(item.get("candidate_id")) == candidate_id), None)
    if candidate is None:
        raise KeyError("Image candidate not found")
    if candidate.get("status") not in (None, "pending_approval"):
        raise ValueError("Only pending candidates can be approved")

    root = Path(image_root).resolve()
    candidate_path = Path(str(candidate.get("image_path") or "")).resolve()
    if root not in candidate_path.parents or not candidate_path.is_file():
        raise ValueError("Candidate image is missing or outside the DARKSTUDIO image directory")
    if candidate_path.stat().st_size <= 0:
        raise ValueError("Candidate image is empty")

    source_scenes = updated.get("_edited_scenes") or updated.get("_source_scenes") or []
    if not isinstance(source_scenes, list):
        raise ValueError("Job scenes are malformed")
    scenes = [dict(item) for item in source_scenes if isinstance(item, dict)]
    position = _find_scene_position(scenes, scene_index)
    scene = scenes[position]

    old_path = scene.get("background_image_path")
    if old_path:
        history = updated.get("scene_asset_history")
        if not isinstance(history, list):
            history = []
            updated["scene_asset_history"] = history
        history.append({
            "history_id": str(uuid4()),
            "scene_index": scene_index,
            "image_path": str(old_path),
            "replaced_by_candidate_id": candidate_id,
            "provider": scene.get("image_asset_provider"),
            "operation": scene.get("image_edit_operation"),
            "prompt": scene.get("visual_prompt"),
            "seed": scene.get("image_generation_seed"),
            "reason": "candidate_approved",
            "created_at": time(),
        })

    scene.update({
        "background_image_path": str(candidate_path),
        "image_asset_provider": candidate.get("provider"),
        "visual_prompt": candidate.get("prompt") or scene.get("visual_prompt"),
        "visual_prompt_full": candidate.get("prompt") or scene.get("visual_prompt_full"),
        "negative_prompt": candidate.get("negative_prompt") or scene.get("negative_prompt", ""),
        "image_edit_operation": candidate.get("operation"),
        "image_generation_seed": candidate.get("seed", -1),
    })
    if updated.get("_edited_scenes") is not None:
        updated["_edited_scenes"] = scenes
    else:
        updated["_edited_scenes"] = scenes

    assets = updated.setdefault("scene_assets", [])
    assets[:] = [
        item for item in assets
        if not (isinstance(item, dict) and int(item.get("scene_index", -1)) == scene_index)
    ]
    assets.append({
        "scene_index": scene_index,
        "image_path": str(candidate_path),
        "image_url": image_url_builder(str(candidate_path)),
        "provider": candidate.get("provider"),
        "status": "edited",
        "operation": candidate.get("operation"),
        "prompt": candidate.get("prompt"),
        "seed": candidate.get("seed", -1),
    })

    remaining = [item for item in bucket if str(item.get("candidate_id")) != candidate_id]
    if remaining:
        updated.setdefault("scene_image_candidates", {})[str(scene_index)] = remaining
    else:
        updated.setdefault("scene_image_candidates", {}).pop(str(scene_index), None)
    updated["scene_image_mode"] = "mixed"

    for clip in updated.get("scene_clips") or []:
        if isinstance(clip, dict) and int(clip.get("scene_index", -1)) == scene_index:
            clip["status"] = "stale"
            clip["reason"] = "A imagem da cena foi aprovada; gere novamente o clipe VidGrid."

    return updated, deepcopy(candidate)



def _history_scene_index(item: dict[str, Any]) -> int:
    try:
        value = item.get("scene_index", -1)
        return -1 if isinstance(value, bool) else int(value)
    except (TypeError, ValueError, OverflowError):
        return -1


def list_scene_image_history(
    record: dict[str, Any], scene_index: int, *, image_root: str | Path, image_url_builder
) -> list[dict[str, Any]]:
    """Return safe, display-ready history entries for one scene."""
    root = Path(image_root).resolve()
    history = record.get("scene_asset_history")
    if not isinstance(history, list):
        return []
    result: list[dict[str, Any]] = []
    for position, item in enumerate(history):
        if not isinstance(item, dict) or _history_scene_index(item) != scene_index:
            continue
        raw_path = str(item.get("image_path") or "").strip()
        available, image_url = False, None
        if raw_path:
            path = Path(raw_path).resolve()
            available = root in path.parents and path.is_file() and path.stat().st_size > 0
            if available:
                try:
                    image_url = image_url_builder(str(path))
                except Exception:
                    available = False
        result.append({
            "history_id": str(item.get("history_id") or f"legacy-{position}"),
            "scene_index": scene_index, "image_url": image_url, "available": available,
            "provider": item.get("provider"), "operation": item.get("operation"),
            "prompt": item.get("prompt"), "reason": item.get("reason"),
            "created_at": item.get("created_at"),
        })
    return result


def restore_scene_image_history(
    record: dict[str, Any], scene_index: int, history_id: str, *,
    image_root: str | Path, image_url_builder,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Restore a previous image, save the current image as an undo entry, and stale one clip."""
    _assert_editable(record)
    if isinstance(scene_index, bool) or not isinstance(scene_index, int) or scene_index < 0:
        raise ValueError("scene_index must be a non-negative integer")
    if not str(history_id or "").strip():
        raise ValueError("history_id is required")
    updated = deepcopy(record)
    history = updated.get("scene_asset_history")
    if not isinstance(history, list):
        raise KeyError("Image history not found")

    selected_position, selected = None, None
    for position, item in enumerate(history):
        if not isinstance(item, dict):
            continue
        item_id = str(item.get("history_id") or f"legacy-{position}")
        if item_id == history_id and _history_scene_index(item) == scene_index:
            selected_position, selected = position, item
            break
    if selected_position is None or selected is None:
        raise KeyError("Image history entry not found")

    root = Path(image_root).resolve()
    previous_path = Path(str(selected.get("image_path") or "")).resolve()
    if root not in previous_path.parents or not previous_path.is_file():
        raise ValueError("Historical image is missing or outside the DARKSTUDIO image directory")
    if previous_path.stat().st_size <= 0:
        raise ValueError("Historical image is empty")

    source_scenes = updated.get("_edited_scenes") or updated.get("_source_scenes") or []
    if not isinstance(source_scenes, list):
        raise ValueError("Job scenes are malformed")
    scenes = [dict(item) for item in source_scenes if isinstance(item, dict)]
    position = _find_scene_position(scenes, scene_index)
    scene = scenes[position]

    current_raw_path = str(scene.get("background_image_path") or "").strip()
    if current_raw_path:
        current_path = Path(current_raw_path).resolve()
        if root in current_path.parents and current_path.is_file() and current_path.stat().st_size > 0:
            history.append({
                "history_id": str(uuid4()), "scene_index": scene_index,
                "image_path": str(current_path), "provider": scene.get("image_asset_provider"),
                "operation": scene.get("image_edit_operation"), "prompt": scene.get("visual_prompt"),
                "seed": scene.get("image_generation_seed"), "reason": "history_restore_undo",
                "created_at": time(),
            })

    restored_path = str(previous_path)
    scene["background_image_path"] = restored_path
    scene["image_asset_provider"] = selected.get("provider") or scene.get("image_asset_provider")
    scene["image_edit_operation"] = selected.get("operation") or "history_restore"
    if selected.get("prompt"):
        scene["visual_prompt"] = selected["prompt"]
        scene["visual_prompt_full"] = selected["prompt"]
    updated["_edited_scenes"] = scenes

    history.pop(selected_position)
    updated["scene_asset_history"] = history
    assets = updated.setdefault("scene_assets", [])
    assets[:] = [
        item for item in assets
        if not (isinstance(item, dict) and _history_scene_index(item) == scene_index)
    ]
    assets.append({
        "scene_index": scene_index, "image_path": restored_path,
        "image_url": image_url_builder(restored_path),
        "provider": selected.get("provider") or scene.get("image_asset_provider"),
        "status": "edited", "operation": selected.get("operation") or "history_restore",
        "prompt": selected.get("prompt") or scene.get("visual_prompt"),
        "seed": selected.get("seed", scene.get("image_generation_seed", -1)),
    })
    updated["scene_image_mode"] = "mixed"
    for clip in updated.get("scene_clips") or []:
        if isinstance(clip, dict) and _history_scene_index(clip) == scene_index:
            clip["status"] = "stale"
            clip["reason"] = "Uma imagem anterior foi restaurada; gere novamente o clipe VidGrid."
    return updated, deepcopy(selected)


def select_scene_character_reference(
    scene: dict[str, Any], profiles: dict[str, Any]
) -> dict[str, str]:
    """Select one explicitly approved reference for a single-character scene.

    AUTOMATIC1111 img2img accepts one init image in this integration. Scenes
    containing zero or multiple assigned characters must use another workflow
    rather than silently conditioning on an arbitrary character.
    """
    raw_ids = scene.get("character_ids")
    if not isinstance(raw_ids, list):
        raise ValueError("Scene must explicitly declare character_ids")
    character_ids = list(dict.fromkeys(
        item.strip() for item in raw_ids if isinstance(item, str) and item.strip()
    ))
    if not character_ids:
        raise ValueError("Scene has no assigned character for reference conditioning")
    if len(character_ids) != 1:
        raise ValueError(
            "Scene has multiple characters; select a composition workflow that supports multiple references"
        )
    character_id = character_ids[0]
    profile = profiles.get(character_id)
    if not isinstance(profile, dict):
        raise ValueError(f"Character identity profile is missing: {character_id}")
    registered = profile.get("reference_asset_ids")
    approved = profile.get("approved_reference_asset_ids")
    registered = registered if isinstance(registered, list) else []
    approved = approved if isinstance(approved, list) else []
    available = [
        item for item in dict.fromkeys(str(value) for value in approved)
        if item in registered and item.strip()
    ]
    if not available:
        raise ValueError(f"Character has no approved reference image: {character_id}")
    return {"character_id": character_id, "reference_asset_id": available[0]}
