"""Asset management endpoints — upload, list, delete project assets."""
from __future__ import annotations
import uuid
import os
import mimetypes
from pathlib import Path
from modules.ai_video_studio.core.local_store import PersistentDict
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel
from modules.ai_video_studio.api.urls import to_download_url

router = APIRouter()


class AssetResponse(BaseModel):
    id: str
    project_id: str
    name: str
    asset_type: str
    mime_type: str | None = None
    file_path: str
    file_size_bytes: int
    duration: float | None = None
    width: int | None = None
    height: int | None = None
    codec: str | None = None
    fps: float | None = None
    thumbnail_url: str | None = None
    download_url: str | None = None


class AssetInfo(BaseModel):
    id: str
    project_id: str
    name: str
    asset_type: str
    mime_type: str | None = None
    file_size_bytes: int
    duration: float | None = None
    file_path: str | None = None
    download_url: str | None = None



_assets = PersistentDict("assets")
# Remove only the fixed IDs used by the old bundled demo fixtures. Real user
# records use generated UUIDs and are left untouched.
for _demo_id in ["a1","a2","a3","a4"]:
    if _demo_id in _assets:
        del _assets[_demo_id]

ASSET_TYPE_MAP = {
    "video/mp4": "video", "video/quicktime": "video", "video/webm": "video",
    "audio/mpeg": "audio", "audio/wav": "audio", "audio/ogg": "audio",
    "image/jpeg": "image", "image/png": "image", "image/webp": "image", "image/gif": "image",
    "application/x-subrip": "subtitle", "text/vtt": "subtitle",
}


def sync_video_job_assets(record: dict) -> None:
    """Index real generated media files in the project asset library."""
    project_id = str(record.get("project_id") or "").strip()
    job_id = str(record.get("job_id") or "").strip()
    if not project_id or not job_id:
        return

    candidates: list[tuple[str, str, str, int | None]] = []

    def _scene_index(item: dict) -> int:
        try:
            return int(item.get("scene_index", 0))
        except (TypeError, ValueError):
            return 0

    for item in record.get("scene_assets") or []:
        if isinstance(item, dict):
            index = _scene_index(item)
            candidates.append((f"image-{index}", str(item.get("name") or f"Imagem da cena {index + 1}"), str(item.get("image_path") or ""), index))
    for item in record.get("scene_clips") or []:
        if isinstance(item, dict):
            index = _scene_index(item)
            candidates.append((f"clip-{index}", str(item.get("name") or f"Clipe da cena {index + 1}"), str(item.get("output_path") or item.get("generative_video_path") or ""), index))
    subtitles = record.get("subtitles")
    if isinstance(subtitles, dict):
        candidates.append(("subtitles", "Legendas", str(subtitles.get("file_path") or ""), None))
    voiceover = record.get("voiceover")
    if isinstance(voiceover, dict):
        # The production generator stores narration as one file per scene.
        for clip in voiceover.get("clips") or []:
            if not isinstance(clip, dict):
                continue
            try:
                index = int(clip.get("index", 0))
            except (TypeError, ValueError):
                continue
            candidates.append((f"narration-{index}", f"Narração da cena {index + 1}", str(clip.get("audio_path") or ""), index))
        # Also index a single-track narration when the selected mode uses one.
        candidates.append(("voiceover", "Narração", str(voiceover.get("output_path") or voiceover.get("file_path") or voiceover.get("audio_path") or ""), None))
    candidates.append(("master-video", "Vídeo final", str(record.get("output_path") or ""), None))

    for key, name, raw_path, scene_index in candidates:
        if not raw_path:
            continue
        path = Path(raw_path).expanduser()
        if not path.is_file():
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        asset_type = (
            "image" if mime_type.startswith("image/")
            else "audio" if mime_type.startswith("audio/")
            else "subtitle" if path.suffix.lower() in {".srt", ".vtt", ".ass"}
            else "video" if mime_type.startswith("video/")
            else "other"
        )
        asset_id = f"job:{job_id}:{key}"
        current = dict(_assets.get(asset_id, {}))
        current.update({
            "id": asset_id,
            "project_id": project_id,
            "name": name,
            "asset_type": asset_type,
            "mime_type": mime_type,
            "file_path": str(path.resolve()),
            "file_size_bytes": size,
            "duration": None,
            "width": None,
            "height": None,
            "codec": None,
            "fps": None,
            "thumbnail_url": None,
            "download_url": to_download_url(str(path.resolve())),
            "_source_job_id": job_id,
            "_source_scene_index": scene_index,
        })
        if current != _assets.get(asset_id):
            _assets[asset_id] = current


@router.post("/upload", response_model=AssetResponse, status_code=201)
async def upload_asset(project_id: str = Query(...), file: UploadFile = File(...)):
    asset_id = str(uuid.uuid4())
    asset_type = ASSET_TYPE_MAP.get(file.content_type or "", "video")
    file_path = f"storage/video_studio/projects/{project_id}/assets/{asset_id}_{file.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    asset = {
        "id": asset_id, "project_id": project_id, "name": file.filename or "unnamed",
        "asset_type": asset_type, "mime_type": file.content_type, "file_path": file_path,
        "file_size_bytes": len(content), "duration": None, "width": None, "height": None,
        "codec": None, "fps": None, "thumbnail_url": None, "download_url": to_download_url(file_path),
    }
    _assets[asset_id] = asset
    return AssetResponse(**asset)


@router.get("/", response_model=list[AssetInfo])
async def list_assets(project_id: str | None = Query(None), asset_type: str | None = None):
    items = list(_assets.values())
    if project_id:
        items = [a for a in items if a["project_id"] == project_id]
    if asset_type:
        items = [a for a in items if a["asset_type"] == asset_type]
    return [AssetInfo(**a) for a in items]


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: str):
    if asset_id not in _assets:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    return AssetResponse(**_assets[asset_id])


@router.delete("/{asset_id}", status_code=204)
async def delete_asset(asset_id: str):
    if asset_id not in _assets:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    a = _assets.pop(asset_id)
    try:
        if os.path.exists(a["file_path"]):
            os.remove(a["file_path"])
    except OSError:
        pass
