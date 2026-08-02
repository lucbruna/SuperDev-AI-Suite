"""Subtitle management endpoints."""
from __future__ import annotations
import uuid
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()


class SubtitleCreate(BaseModel):
    project_id: str
    scene_id: str | None = None
    text: str = Field(..., min_length=1, max_length=2000)
    language: str = "en"
    start_time: float = 0.0
    end_time: float = 0.0
    duration: float = 0.0
    font_name: str = "Arial"
    font_size: int = 24
    font_color: str = "#FFFFFF"
    background_color: str | None = None
    position_x: float = 0.5
    position_y: float = 0.9
    alignment: str = "center"
    border_width: int = 2


class SubtitleUpdate(BaseModel):
    text: str | None = None
    language: str | None = None
    start_time: float | None = None
    end_time: float | None = None
    duration: float | None = None
    font_name: str | None = None
    font_size: int | None = None
    font_color: str | None = None
    background_color: str | None = None
    position_x: float | None = None
    position_y: float | None = None
    alignment: str | None = None
    border_width: int | None = None


class SubtitleResponse(BaseModel):
    id: str
    project_id: str
    scene_id: str | None = None
    text: str
    language: str
    start_time: float
    end_time: float
    duration: float
    font_name: str
    font_size: int
    font_color: str
    background_color: str | None
    position_x: float
    position_y: float
    alignment: str
    border_width: int
    is_translation: bool
    word_count: int


class AutoSubtitleRequest(BaseModel):
    project_id: str
    scene_id: str | None = None
    audio_text: str = Field(..., min_length=1, max_length=10000)
    language: str = "en"
    max_chars_per_line: int = 42
    words_per_subtitle: int = 8


class TranslateRequest(BaseModel):
    subtitle_id: str
    target_language: str


class GenerateSrtScene(BaseModel):
    text: str = ""
    duration: float = 3.0


class GenerateSrtRequest(BaseModel):
    scenes: list[GenerateSrtScene] = Field(..., min_length=1)
    max_chars_per_line: int = 42


class GenerateSrtResponse(BaseModel):
    file_path: str
    content: str
    cue_count: int
    duration: float


_subtitles: dict[str, dict] = {}


@router.post("/", response_model=SubtitleResponse, status_code=201)
async def create_subtitle(data: SubtitleCreate):
    sid = str(uuid.uuid4())
    wc = len(data.text.split())
    sub = {"id": sid, **data.model_dump(), "is_translation": False, "word_count": wc}
    _subtitles[sid] = sub
    return SubtitleResponse(**sub)


@router.get("/", response_model=list[SubtitleResponse])
async def list_subtitles(project_id: str = Query(...), scene_id: str | None = None, language: str | None = None):
    items = [s for s in _subtitles.values() if s["project_id"] == project_id]
    if scene_id:
        items = [s for s in items if s["scene_id"] == scene_id]
    if language:
        items = [s for s in items if s["language"] == language]
    items.sort(key=lambda s: s["start_time"])
    return [SubtitleResponse(**s) for s in items]


@router.get("/{subtitle_id}", response_model=SubtitleResponse)
async def get_subtitle(subtitle_id: str):
    if subtitle_id not in _subtitles:
        raise HTTPException(status_code=404, detail=f"Subtitle {subtitle_id} not found")
    return SubtitleResponse(**_subtitles[subtitle_id])


@router.patch("/{subtitle_id}", response_model=SubtitleResponse)
async def update_subtitle(subtitle_id: str, data: SubtitleUpdate):
    if subtitle_id not in _subtitles:
        raise HTTPException(status_code=404, detail=f"Subtitle {subtitle_id} not found")
    _subtitles[subtitle_id].update(data.model_dump(exclude_unset=True))
    s = _subtitles[subtitle_id]
    s["word_count"] = len(s["text"].split())
    return SubtitleResponse(**s)


@router.delete("/{subtitle_id}", status_code=204)
async def delete_subtitle(subtitle_id: str):
    if subtitle_id not in _subtitles:
        raise HTTPException(status_code=404, detail=f"Subtitle {subtitle_id} not found")
    del _subtitles[subtitle_id]


@router.post("/auto-generate", response_model=list[SubtitleResponse], status_code=201)
async def auto_generate_subtitles(req: AutoSubtitleRequest):
    """Auto-generate subtitles from text by splitting into timed segments."""
    words = req.audio_text.split()
    subs = []
    time_offset = 0.0
    words_per_sub = req.words_per_subtitle
    chars_per_sub = req.max_chars_per_line
    for i in range(0, len(words), words_per_sub):
        chunk = words[i:i + words_per_sub]
        text = " ".join(chunk)
        if len(text) > chars_per_sub:
            text = text[:chars_per_sub]
        duration = len(chunk) * 0.45
        sid = str(uuid.uuid4())
        sub = {
            "id": sid, "project_id": req.project_id, "scene_id": req.scene_id,
            "text": text, "language": req.language, "start_time": time_offset,
            "end_time": time_offset + duration, "duration": duration,
            "font_name": "Arial", "font_size": 24, "font_color": "#FFFFFF",
            "background_color": None, "position_x": 0.5, "position_y": 0.9,
            "alignment": "center", "border_width": 2, "is_translation": False,
            "word_count": len(chunk),
        }
        _subtitles[sid] = sub
        subs.append(SubtitleResponse(**sub))
        time_offset += duration
    return subs


@router.post("/translate", response_model=SubtitleResponse, status_code=201)
async def translate_subtitle(req: TranslateRequest):
    """Create a translated copy of a subtitle.

    Uses the platform LLM when a provider is configured; falls back to a
    deterministic copy otherwise (never fails).
    """
    if req.subtitle_id not in _subtitles:
        raise HTTPException(status_code=404, detail=f"Subtitle {req.subtitle_id} not found")
    orig = _subtitles[req.subtitle_id]

    from modules.ai_video_studio.services.subtitle_studio import SubtitleStudioService

    translated_text = orig["text"]
    try:
        translated = await SubtitleStudioService().translate(
            orig["text"], req.target_language
        )
        if translated["engine"] == "llm":
            translated_text = translated["text"]
    except Exception:  # noqa: BLE001 — translation is best-effort
        pass

    sid = str(uuid.uuid4())
    translated = {
        "id": sid, "project_id": orig["project_id"], "scene_id": orig["scene_id"],
        "text": translated_text, "language": req.target_language,
        "start_time": orig["start_time"], "end_time": orig["end_time"], "duration": orig["duration"],
        "font_name": orig["font_name"], "font_size": orig["font_size"],
        "font_color": orig["font_color"], "background_color": orig["background_color"],
        "position_x": orig["position_x"], "position_y": orig["position_y"],
        "alignment": orig["alignment"], "border_width": orig["border_width"],
        "is_translation": True, "word_count": len(translated_text.split()),
    }
    _subtitles[sid] = translated
    return SubtitleResponse(**translated)


@router.post("/generate-srt", response_model=GenerateSrtResponse, status_code=201)
async def generate_srt(req: GenerateSrtRequest):
    """Generate a timed SRT subtitle file from scene narration.

    Timing is computed per scene using a reading-speed model, so cues align
    with the rendered video duration.
    """
    from modules.ai_video_studio.services.subtitle_studio import SubtitleStudioService

    scenes = [s.model_dump() for s in req.scenes]
    result = SubtitleStudioService().generate_srt(
        scenes, max_chars=req.max_chars_per_line
    )
    return GenerateSrtResponse(
        file_path=result["file_path"],
        content=SubtitleStudioService.read_srt(result["file_path"]),
        cue_count=result["cue_count"],
        duration=result["duration"],
    )
