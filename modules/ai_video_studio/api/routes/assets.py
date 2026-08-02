"""Asset management endpoints — upload, list, delete project assets."""
from __future__ import annotations
import uuid
import os
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel, Field

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

ASSET_TYPE_MAP = {
    "video/mp4": "video", "video/quicktime": "video", "video/webm": "video",
    "audio/mpeg": "audio", "audio/wav": "audio", "audio/ogg": "audio",
    "image/jpeg": "image", "image/png": "image", "image/webp": "image", "image/gif": "image",
    "application/x-subrip": "subtitle", "text/vtt": "subtitle",
}


@router.post("/upload", response_model=AssetResponse, status_code=201)
async def upload_asset(project_id: str = Query(...), file: UploadFile = File(...)):
    asset_id = str(uuid.uuid4())
    asset_type = ASSET_TYPE_MAP.get(file.content_type, "video")
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
async def list_assets(project_id: str = Query(...), asset_type: str | None = None):
    items = [a for a in _assets.values() if a["project_id"] == project_id]
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
