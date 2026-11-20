"""Scene CRUD endpoints."""
from __future__ import annotations
import uuid
from modules.ai_video_studio.core.local_store import PersistentDict
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()


class SceneCreate(BaseModel):
    project_id: str
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    order_index: int = 0
    scene_type: str = "content"
    duration: float = 5.0
    script: str | None = None
    visual_prompt: str | None = None
    voiceover_text: str | None = None
    background_color: str | None = None
    transition_in: str = "cut"
    transition_out: str = "cut"
    transition_duration: float = 0.5


class SceneUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    order_index: int | None = None
    scene_type: str | None = None
    duration: float | None = None
    script: str | None = None
    visual_prompt: str | None = None
    voiceover_text: str | None = None
    background_color: str | None = None
    transition_in: str | None = None
    transition_out: str | None = None
    transition_duration: float | None = None
    generation_status: str | None = None
    generated_video_url: str | None = None
    generated_image_url: str | None = None


class SceneResponse(BaseModel):
    id: str
    project_id: str
    name: str
    description: str | None = None
    order_index: int
    scene_type: str
    start_time: float
    duration: float
    end_time: float
    script: str | None = None
    visual_prompt: str | None = None
    voiceover_text: str | None = None
    background_color: str | None = None
    transition_in: str
    transition_out: str
    transition_duration: float
    generation_status: str
    generated_video_url: str | None = None
    generated_image_url: str | None = None


_scenes: dict[str, dict] = PersistentDict("scenes")


def sync_video_job_scenes(record: dict) -> None:
    """Upsert generated scenes into the editable project scene catalog."""
    project_id = str(record.get("project_id") or "").strip()
    job_id = str(record.get("job_id") or "").strip()
    if not project_id or not job_id:
        return

    scenes = record.get("_edited_scenes") or record.get("_source_scenes") or []
    if not isinstance(scenes, list):
        return
    assets = record.get("scene_assets") or []
    clips = record.get("scene_clips") or []
    progress = record.get("scene_progress") or []
    offset = 0.0
    for position, source in enumerate(scenes):
        if not isinstance(source, dict) or not source:
            continue
        try:
            index = int(source.get("_source_scene_index", position))
        except (TypeError, ValueError):
            index = position
        scene_id = f"job:{job_id}:{index}"
        duration = 10.0 if record.get("vidgrid_compatible") else float(source.get("duration") or 5.0)
        asset = next((item for item in assets if int(item.get("scene_index", -1)) == index), {})
        clip = next((item for item in clips if int(item.get("scene_index", -1)) == index), {})
        progress_item = next((item for item in progress if int(item.get("scene_index", -1)) == index), {})
        existing = _scenes.get(scene_id, {})
        protected = set(existing.get("_user_modified_fields") or [])
        values = {
            "id": scene_id,
            "project_id": project_id,
            "name": source.get("title") or source.get("name") or f"Cena {index + 1}",
            "description": source.get("description") or source.get("visual_prompt"),
            "order_index": index,
            "scene_type": source.get("scene_type") or "content",
            "start_time": offset,
            "duration": duration,
            "end_time": offset + duration,
            "script": source.get("script") or source.get("narration") or source.get("voiceover_text"),
            "visual_prompt": source.get("visual_prompt") or source.get("description"),
            "voiceover_text": source.get("voiceover_text") or source.get("narration") or source.get("dialogue"),
            "background_color": source.get("background_color"),
            "transition_in": source.get("transition_in") or "cut",
            "transition_out": source.get("transition_out") or "cut",
            "transition_duration": float(source.get("transition_duration") or 0.5),
            "generation_status": (
                "completed" if clip.get("output_url") or clip.get("output_path")
                else "processing" if progress_item.get("status") == "processing"
                else "failed" if progress_item.get("status") == "failed"
                else "completed" if asset.get("image_url") or asset.get("image_path")
                else "pending"
            ),
            "generated_video_url": clip.get("output_url") or clip.get("generative_video_url"),
            "generated_image_url": asset.get("image_url"),
            "_source_job_id": job_id,
            "_source_scene_index": index,
            "_user_modified_fields": list(protected),
        }
        for key, value in values.items():
            if key not in protected or key.startswith("_"):
                existing[key] = value
        _scenes[scene_id] = existing
        offset += duration


@router.post("/", response_model=SceneResponse, status_code=201)
async def create_scene(data: SceneCreate):
    sid = str(uuid.uuid4())
    start = 0.0
    existing = [s for s in _scenes.values() if s["project_id"] == data.project_id]
    if existing:
        start = max(s["end_time"] for s in existing)
    scene = {
        "id": sid, **data.model_dump(), "start_time": start, "end_time": start + data.duration,
        "generation_status": "pending", "generated_video_url": None, "generated_image_url": None,
    }
    _scenes[sid] = scene
    return SceneResponse(**scene)


@router.get("/", response_model=list[SceneResponse])
async def list_scenes(project_id: str = Query(...), limit: int = Query(100, ge=1, le=500)):
    items = sorted(
        [s for s in _scenes.values() if s["project_id"] == project_id],
        key=lambda s: s["order_index"]
    )
    return [SceneResponse(**s) for s in items[:limit]]


@router.get("/{scene_id}", response_model=SceneResponse)
async def get_scene(scene_id: str):
    if scene_id not in _scenes:
        raise HTTPException(status_code=404, detail=f"Scene {scene_id} not found")
    return SceneResponse(**_scenes[scene_id])


@router.patch("/{scene_id}", response_model=SceneResponse)
async def update_scene(scene_id: str, data: SceneUpdate):
    if scene_id not in _scenes:
        raise HTTPException(status_code=404, detail=f"Scene {scene_id} not found")
    updates = data.model_dump(exclude_unset=True)
    scene = _scenes[scene_id]
    scene.update(updates)
    modified = set(scene.get("_user_modified_fields") or [])
    modified.update(updates)
    scene["_user_modified_fields"] = sorted(modified)
    s = scene
    s["end_time"] = s["start_time"] + s["duration"]
    return SceneResponse(**s)


@router.delete("/{scene_id}", status_code=204)
async def delete_scene(scene_id: str):
    if scene_id not in _scenes:
        raise HTTPException(status_code=404, detail=f"Scene {scene_id} not found")
    del _scenes[scene_id]


@router.post("/{scene_id}/reorder")
async def reorder_scene(scene_id: str, new_index: int = Query(..., ge=0)):
    if scene_id not in _scenes:
        raise HTTPException(status_code=404, detail=f"Scene {scene_id} not found")
    pid = _scenes[scene_id]["project_id"]
    siblings = sorted(
        [s for s in _scenes.values() if s["project_id"] == pid],
        key=lambda s: s["order_index"]
    )
    current = next((i for i, s in enumerate(siblings) if s["id"] == scene_id), None)
    if current is None:
        raise HTTPException(status_code=500, detail="Scene not in sibling list")
    siblings.pop(current)
    siblings.insert(min(new_index, len(siblings)), _scenes[scene_id])
    offset = 0.0
    for i, s in enumerate(siblings):
        s["order_index"] = i
        s["start_time"] = offset
        s["end_time"] = offset + s["duration"]
        offset = s["end_time"]
    return {"message": "Reordered", "new_index": new_index}
