"""Audio track endpoints — voice, music, SFX management."""
from __future__ import annotations
import uuid
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()


class AudioTrackCreate(BaseModel):
    project_id: str
    scene_id: str | None = None
    name: str = Field(..., min_length=1, max_length=255)
    track_type: str = "voice_over"
    file_path: str | None = None
    duration: float = 0.0
    start_time: float = 0.0
    volume: float = 1.0
    fade_in: float = 0.0
    fade_out: float = 0.0
    is_loop: bool = False
    voice_id: str | None = None
    voice_speed: float = 1.0
    voice_pitch: float = 1.0
    emotion: str | None = None


class AudioTrackUpdate(BaseModel):
    name: str | None = None
    track_type: str | None = None
    file_path: str | None = None
    duration: float | None = None
    start_time: float | None = None
    volume: float | None = None
    fade_in: float | None = None
    fade_out: float | None = None
    is_muted: bool | None = None
    is_loop: bool | None = None
    voice_id: str | None = None
    voice_speed: float | None = None
    voice_pitch: float | None = None
    emotion: str | None = None


class AudioTrackResponse(BaseModel):
    id: str
    project_id: str
    scene_id: str | None = None
    name: str
    track_type: str
    file_path: str | None = None
    duration: float
    start_time: float
    volume: float
    fade_in: float
    fade_out: float
    is_muted: bool
    is_loop: bool
    voice_id: str | None = None
    voice_speed: float
    voice_pitch: float
    emotion: str | None = None


class VoiceSynthesizeRequest(BaseModel):
    project_id: str
    scene_id: str | None = None
    text: str = Field(..., min_length=1, max_length=5000)
    voice_id: str = "default"
    language: str = "en"
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    pitch: float = Field(default=1.0, ge=0.5, le=2.0)
    emotion: str | None = None


_audio: dict[str, dict] = {}


@router.post("/", response_model=AudioTrackResponse, status_code=201)
async def create_audio_track(data: AudioTrackCreate):
    aid = str(uuid.uuid4())
    track = {"id": aid, **data.model_dump(), "is_muted": False}
    _audio[aid] = track
    return AudioTrackResponse(**track)


@router.get("/", response_model=list[AudioTrackResponse])
async def list_audio_tracks(project_id: str = Query(...), track_type: str | None = None, scene_id: str | None = None):
    items = [t for t in _audio.values() if t["project_id"] == project_id]
    if track_type:
        items = [t for t in items if t["track_type"] == track_type]
    if scene_id:
        items = [t for t in items if t["scene_id"] == scene_id]
    return [AudioTrackResponse(**t) for t in items]


@router.get("/{track_id}", response_model=AudioTrackResponse)
async def get_audio_track(track_id: str):
    if track_id not in _audio:
        raise HTTPException(status_code=404, detail=f"Audio track {track_id} not found")
    return AudioTrackResponse(**_audio[track_id])


@router.patch("/{track_id}", response_model=AudioTrackResponse)
async def update_audio_track(track_id: str, data: AudioTrackUpdate):
    if track_id not in _audio:
        raise HTTPException(status_code=404, detail=f"Audio track {track_id} not found")
    _audio[track_id].update(data.model_dump(exclude_unset=True))
    return AudioTrackResponse(**_audio[track_id])


@router.delete("/{track_id}", status_code=204)
async def delete_audio_track(track_id: str):
    if track_id not in _audio:
        raise HTTPException(status_code=404, detail=f"Audio track {track_id} not found")
    del _audio[track_id]


@router.post("/synthesize", response_model=AudioTrackResponse, status_code=201)
async def synthesize_voice(req: VoiceSynthesizeRequest):
    """Generate a voice-over from text using AI TTS."""
    aid = str(uuid.uuid4())
    track = {
        "id": aid, "project_id": req.project_id, "scene_id": req.scene_id,
        "name": f"Voice: {req.text[:40]}...", "track_type": "voice_over",
        "file_path": None, "duration": len(req.text) * 0.06, "start_time": 0.0,
        "volume": 1.0, "fade_in": 0.0, "fade_out": 0.0, "is_muted": False, "is_loop": False,
        "voice_id": req.voice_id, "voice_speed": req.speed, "voice_pitch": req.pitch,
        "emotion": req.emotion,
    }
    _audio[aid] = track
    return AudioTrackResponse(**track)
