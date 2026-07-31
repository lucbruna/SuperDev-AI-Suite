"""Export/Import API routes."""

from __future__ import annotations

from typing import Any

from backend.dependencies import get_current_active_user
from backend.export_import.data_exporter import ExportFormat, exporter, importer
from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

router = APIRouter(dependencies=[Depends(get_current_active_user)])


class ExportRequest(BaseModel):
    data: list[dict[str, Any]]
    format: str = "json"
    filename: str | None = None


class ImportJsonRequest(BaseModel):
    json_string: str | None = None
    file_path: str | None = None


class ImportCsvRequest(BaseModel):
    csv_string: str | None = None
    file_path: str | None = None


@router.post("/export")
async def export_data(
    request: ExportRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    fmt = ExportFormat(request.format)
    if fmt == ExportFormat.JSON:
        result = exporter.export_json(request.data, request.filename)
    elif fmt == ExportFormat.CSV:
        result = exporter.export_csv(request.data, request.filename)
    elif fmt == ExportFormat.XLSX:
        result = exporter.export_xlsx(request.data, request.filename)
    else:
        return {"success": False, "error": f"Unsupported format: {request.format}"}

    return {
        "success": result.success,
        "export_id": result.export_id,
        "record_count": result.record_count,
        "file_path": result.file_path,
        "file_size": result.file_size,
        "error": result.error,
    }


@router.post("/export/string")
async def export_to_string(
    request: ExportRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> PlainTextResponse:
    fmt = ExportFormat(request.format)
    content = exporter.export_to_string(request.data, fmt)
    media_type = "application/json" if fmt == ExportFormat.JSON else "text/csv"
    return PlainTextResponse(content=content, media_type=media_type)


@router.post("/import/json")
async def import_json(
    request: ImportJsonRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    result = importer.import_json(file_path=request.file_path, json_string=request.json_string)
    return {
        "success": result.success,
        "import_id": result.import_id,
        "records_imported": result.records_imported,
        "errors": result.errors,
    }


@router.post("/import/csv")
async def import_csv(
    request: ImportCsvRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    result = importer.import_csv(file_path=request.file_path, csv_string=request.csv_string)
    return {
        "success": result.success,
        "import_id": result.import_id,
        "records_imported": result.records_imported,
        "errors": result.errors,
    }


@router.get("/exports")
async def list_exports(
    limit: int = Query(default=50, le=200),
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    exports = exporter.list_exports(limit=limit)
    return {
        "exports": [
            {
                "id": e.export_id,
                "format": e.format.value,
                "record_count": e.record_count,
                "file_path": e.file_path,
                "file_size": e.file_size,
                "success": e.success,
            }
            for e in exports
        ]
    }


@router.get("/imports")
async def list_imports(
    limit: int = Query(default=50, le=200),
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    imports = importer.list_imports(limit=limit)
    return {
        "imports": [
            {
                "id": i.import_id,
                "format": i.format.value,
                "records_imported": i.records_imported,
                "success": i.success,
                "errors": i.errors,
            }
            for i in imports
        ]
    }


@router.get("/stats")
async def export_import_stats(
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    return {
        "export": exporter.get_stats(),
        "import": importer.get_stats(),
    }
