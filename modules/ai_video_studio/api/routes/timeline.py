"""Timeline endpoints — manage multi-track video timelines."""
from __future__ import annotations
import uuid
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()


class TimelineCreate(BaseModel):
    project_id: str
    name: str = "Main Timeline"
    track_type: str = "video"
    fps: int = 30


class ClipCreate(BaseModel):
    scene_id: str
    start: float = Field(..., ge=0.0)
    end: float = Field(..., gt=0.0)
    trim_start: float = Field(default=0.0, ge=0.0)
    trim_end: float = Field(default=0.0, ge=0.0)


class ClipResponse(BaseModel):
    scene_id: str
    start: float
    end: float
    trim_start: float
    trim_end: float


class TimelineResponse(BaseModel):
    id: str
    project_id: str
    name: str
    track_type: str
    order_index: int
    is_muted: bool
    is_locked: bool
    volume: float
    total_duration: float
    fps: int
    clips: list[ClipResponse]


_timelines: dict[str, dict] = {}


@router.post("/", response_model=TimelineResponse, status_code=201)
async def create_timeline(data: TimelineCreate):
    tid = str(uuid.uuid4())
    tl = {
        "id": tid, "project_id": data.project_id, "name": data.name,
        "track_type": data.track_type, "order_index": 0, "is_muted": False,
        "is_locked": False, "volume": 1.0, "total_duration": 0.0,
        "fps": data.fps, "clips": [],
    }
    _timelines[tid] = tl
    return TimelineResponse(**tl)


@router.get("/", response_model=list[TimelineResponse])
async def list_timelines(project_id: str = Query(...)):
    items = [t for t in _timelines.values() if t["project_id"] == project_id]
    return [TimelineResponse(**t) for t in items]


@router.get("/{timeline_id}", response_model=TimelineResponse)
async def get_timeline(timeline_id: str):
    if timeline_id not in _timelines:
        raise HTTPException(status_code=404, detail=f"Timeline {timeline_id} not found")
    return TimelineResponse(**_timelines[timeline_id])


@router.post("/{timeline_id}/clips", response_model=TimelineResponse)
async def add_clip(timeline_id: str, clip: ClipCreate):
    if timeline_id not in _timelines:
        raise HTTPException(status_code=404, detail=f"Timeline {timeline_id} not found")
    tl = _timelines[timeline_id]
    if tl["is_locked"]:
        raise HTTPException(status_code=400, detail="Timeline is locked")
    clip_dict = clip.model_dump()
    tl["clips"].append(clip_dict)
    tl["total_duration"] = max(tl["total_duration"], clip.end)
    return TimelineResponse(**tl)


@router.delete("/{timeline_id}/clips/{scene_id}")
async def remove_clip(timeline_id: str, scene_id: str):
    if timeline_id not in _timelines:
        raise HTTPException(status_code=404, detail=f"Timeline {timeline_id} not found")
    tl = _timelines[timeline_id]
    if tl["is_locked"]:
        raise HTTPException(status_code=400, detail="Timeline is locked")
    before = len(tl["clips"])
    tl["clips"] = [c for c in tl["clips"] if c["scene_id"] != scene_id]
    if len(tl["clips"]) == before:
        raise HTTPException(status_code=404, detail=f"Clip with scene {scene_id} not found")
    tl["total_duration"] = max((c["end"] for c in tl["clips"]), default=0.0)
    return {"message": "Clip removed"}


@router.patch("/{timeline_id}/volume")
async def set_volume(timeline_id: str, volume: float = Query(..., ge=0.0, le=2.0)):
    if timeline_id not in _timelines:
        raise HTTPException(status_code=404, detail=f"Timeline {timeline_id} not found")
    _timelines[timeline_id]["volume"] = volume
    return {"volume": volume}


@router.delete("/{timeline_id}", status_code=204)
async def delete_timeline(timeline_id: str):
    if timeline_id not in _timelines:
        raise HTTPException(status_code=404, detail=f"Timeline {timeline_id} not found")
    del _timelines[timeline_id]
