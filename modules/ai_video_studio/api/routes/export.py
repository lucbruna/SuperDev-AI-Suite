"""Export endpoints — multi-format export of rendered videos."""
from __future__ import annotations
import uuid
from datetime import UTC, datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from modules.ai_video_studio.core.exceptions import ExportFormatError

router = APIRouter()


class ExportCreate(BaseModel):
    input_path: str = Field(..., min_length=1)
    format: str = "mp4"
    scale: str | None = None


class ExportResponse(BaseModel):
    id: str
    input_path: str
    format: str
    file_path: str | None = None
    file_size_bytes: int = 0
    duration: float = 0.0
    status: str
    error: str | None = None
    created_at: str


class ExportFormatsResponse(BaseModel):
    id: str
    container: str
    extension: str
    description: str


_exports: dict[str, dict] = {}


@router.get("/formats", response_model=list[ExportFormatsResponse])
async def list_export_formats():
    """List the supported export formats."""
    from modules.ai_video_studio.services.export_service import ExportService

    return [ExportFormatsResponse(**f) for f in ExportService().list_formats()]


@router.post("/", response_model=ExportResponse, status_code=201)
async def create_export(data: ExportCreate):
    """Export a rendered video to the requested format (real FFmpeg transcode)."""
    from modules.ai_video_studio.services.export_service import ExportService

    eid = str(uuid.uuid4())
    record = {
        "id": eid, "input_path": data.input_path, "format": data.format,
        "file_path": None, "file_size_bytes": 0, "duration": 0.0,
        "status": "queued", "error": None,
        "created_at": datetime.now(UTC).isoformat(),
    }
    _exports[eid] = record

    try:
        result = await ExportService().export(
            data.input_path, data.format, scale=data.scale
        )
        record.update(
            status="completed",
            file_path=result["file_path"],
            file_size_bytes=result["file_size_bytes"],
            duration=result["duration"],
        )
    except ExportFormatError as e:
        record.update(status="failed", error=e.to_dict())
        raise HTTPException(status_code=e.status_code, detail=e.to_dict()) from e
    except Exception as e:  # noqa: BLE001 — record failure, surface as 500
        record.update(status="failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Export failed: {e}") from e
    return ExportResponse(**record)


@router.get("/", response_model=list[ExportResponse])
async def list_exports(status: str | None = None):
    items = list(_exports.values())
    if status:
        items = [e for e in items if e["status"] == status]
    return [ExportResponse(**e) for e in items]


@router.get("/{export_id}", response_model=ExportResponse)
async def get_export(export_id: str):
    if export_id not in _exports:
        raise HTTPException(status_code=404, detail=f"Export {export_id} not found")
    return ExportResponse(**_exports[export_id])
