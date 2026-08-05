"""Asset management endpoints — upload, list, delete project assets."""
from __future__ import annotations
import uuid
import os
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel

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


class AssetInfo(BaseModel):
    id: str
    project_id: str
    name: str
    asset_type: str
    mime_type: str | None = None
    file_size_bytes: int
    duration: float | None = None


_assets: dict[str, dict] = {}


def _seed_assets() -> dict[str, dict]:
    """Demo assets mirroring the frontend library (in-memory store)."""
    rows: list[dict] = [
        {
            "id": "a1", "project_id": "p1", "name": "hero_broll.mp4",
            "asset_type": "video", "mime_type": "video/mp4",
            "file_path": "storage/video_studio/projects/p1/assets/hero_broll.mp4",
            "file_size_bytes": 4_200_000_000, "duration": 12.4, "width": 3840, "height": 2160,
            "codec": "h264", "fps": 30.0, "thumbnail_url": None,
        },
        {
            "id": "a2", "project_id": "p1", "name": "logo_white.svg",
            "asset_type": "image", "mime_type": "image/svg+xml",
            "file_path": "storage/video_studio/projects/p1/assets/logo_white.svg",
            "file_size_bytes": 18_000, "duration": None, "width": None, "height": None,
            "codec": None, "fps": None, "thumbnail_url": None,
        },
        {
            "id": "a3", "project_id": "p2", "name": "voiceover_final.wav",
            "asset_type": "audio", "mime_type": "audio/wav",
            "file_path": "storage/video_studio/projects/p2/assets/voiceover_final.wav",
            "file_size_bytes": 24_000_000, "duration": 96.0, "width": None, "height": None,
            "codec": "pcm", "fps": None, "thumbnail_url": None,
        },
        {
            "id": "a4", "project_id": "p4", "name": "captions_pt.srt",
            "asset_type": "subtitle", "mime_type": "application/x-subrip",
            "file_path": "storage/video_studio/projects/p4/assets/captions_pt.srt",
            "file_size_bytes": 8_400, "duration": None, "width": None, "height": None,
            "codec": None, "fps": None, "thumbnail_url": None,
        },
    ]
    return {r["id"]: r for r in rows}


_assets = _seed_assets()

ASSET_TYPE_MAP = {
    "video/mp4": "video", "video/quicktime": "video", "video/webm": "video",
    "audio/mpeg": "audio", "audio/wav": "audio", "audio/ogg": "audio",
    "image/jpeg": "image", "image/png": "image", "image/webp": "image", "image/gif": "image",
    "application/x-subrip": "subtitle", "text/vtt": "subtitle",
}


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
        "codec": None, "fps": None, "thumbnail_url": None,
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
