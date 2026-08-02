"""Scene CRUD endpoints."""
from __future__ import annotations
import uuid
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


_scenes: dict[str, dict] = {}


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
    _scenes[scene_id].update(data.model_dump(exclude_unset=True))
    s = _scenes[scene_id]
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
