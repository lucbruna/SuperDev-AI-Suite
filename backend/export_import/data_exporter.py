"""Data export/import service supporting JSON, CSV, and Excel formats."""

from __future__ import annotations

import csv
import io
import json
import logging
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

from backend.utils.uuid_utils import generate_uuid

logger = logging.getLogger(__name__)


class ExportFormat(StrEnum):
    JSON = "json"
    CSV = "csv"
    XLSX = "xlsx"


class ImportFormat(StrEnum):
    JSON = "json"
    CSV = "csv"


@dataclass
class ExportResult:
    success: bool
    export_id: str
    format: ExportFormat
    file_path: str | None = None
    record_count: int = 0
    file_size: int = 0
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ImportResult:
    success: bool
    import_id: str
    format: ImportFormat
    records_imported: int = 0
    records_skipped: int = 0
    records_failed: int = 0
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class DataExporter:
    """Export data in multiple formats."""

    def __init__(self, export_dir: str = "exports"):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self._exports: dict[str, ExportResult] = {}

    def export_json(
        self,
        data: list[dict[str, Any]],
        filename: str | None = None,
        pretty: bool = True,
    ) -> ExportResult:
        export_id = generate_uuid()
        try:
            fname = filename or f"export_{export_id}.json"
            file_path = self.export_dir / fname

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2 if pretty else None, default=str, ensure_ascii=False)

            result = ExportResult(
                success=True,
                export_id=export_id,
                format=ExportFormat.JSON,
                file_path=str(file_path),
                record_count=len(data),
                file_size=file_path.stat().st_size,
            )
            self._exports[export_id] = result
            return result

        except Exception as e:
            result = ExportResult(success=False, export_id=export_id, format=ExportFormat.JSON, error=str(e))
            self._exports[export_id] = result
            return result

    def export_csv(
        self,
        data: list[dict[str, Any]],
        filename: str | None = None,
        delimiter: str = ",",
    ) -> ExportResult:
        export_id = generate_uuid()
        try:
            if not data:
                return ExportResult(success=True, export_id=export_id, format=ExportFormat.CSV, record_count=0)

            fname = filename or f"export_{export_id}.csv"
            file_path = self.export_dir / fname

            headers = list(data[0].keys())
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers, delimiter=delimiter)
                writer.writeheader()
                writer.writerows(data)

            result = ExportResult(
                success=True,
                export_id=export_id,
                format=ExportFormat.CSV,
                file_path=str(file_path),
                record_count=len(data),
                file_size=file_path.stat().st_size,
            )
            self._exports[export_id] = result
            return result

        except Exception as e:
            result = ExportResult(success=False, export_id=export_id, format=ExportFormat.CSV, error=str(e))
            self._exports[export_id] = result
            return result

    def export_xlsx(
        self,
        data: list[dict[str, Any]],
        filename: str | None = None,
        sheet_name: str = "Sheet1",
    ) -> ExportResult:
        export_id = generate_uuid()
        try:
            from openpyxl import Workbook

            fname = filename or f"export_{export_id}.xlsx"
            file_path = self.export_dir / fname

            wb = Workbook()
            ws = wb.active
            ws.title = sheet_name

            if data:
                headers = list(data[0].keys())
                ws.append(headers)
                for row in data:
                    ws.append([row.get(h, "") for h in headers])

            wb.save(file_path)

            result = ExportResult(
                success=True,
                export_id=export_id,
                format=ExportFormat.XLSX,
                file_path=str(file_path),
                record_count=len(data),
                file_size=file_path.stat().st_size,
            )
            self._exports[export_id] = result
            return result

        except ImportError:
            return ExportResult(
                success=False,
                export_id=export_id,
                format=ExportFormat.XLSX,
                error="openpyxl not installed. Run: pip install openpyxl",
            )
        except Exception as e:
            result = ExportResult(success=False, export_id=export_id, format=ExportFormat.XLSX, error=str(e))
            self._exports[export_id] = result
            return result

    def export_to_string(
        self,
        data: list[dict[str, Any]],
        format: ExportFormat = ExportFormat.JSON,
    ) -> str:
        if format == ExportFormat.JSON:
            return json.dumps(data, indent=2, default=str, ensure_ascii=False)
        elif format == ExportFormat.CSV:
            if not data:
                return ""
            output = io.StringIO()
            headers = list(data[0].keys())
            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
            return output.getvalue()
        return ""

    def get_export(self, export_id: str) -> ExportResult | None:
        return self._exports.get(export_id)

    def list_exports(self, limit: int = 50) -> list[ExportResult]:
        return sorted(self._exports.values(), key=lambda r: r.export_id, reverse=True)[:limit]

    def get_stats(self) -> dict[str, Any]:
        return {
            "total_exports": len(self._exports),
            "by_format": {fmt.value: sum(1 for r in self._exports.values() if r.format == fmt) for fmt in ExportFormat},
            "export_dir": str(self.export_dir),
        }


class DataImporter:
    """Import data from JSON and CSV files."""

    def __init__(self, import_dir: str = "imports"):
        self.import_dir = Path(import_dir)
        self.import_dir.mkdir(parents=True, exist_ok=True)
        self._imports: dict[str, ImportResult] = {}

    def import_json(
        self,
        file_path: str | None = None,
        json_string: str | None = None,
    ) -> ImportResult:
        import_id = generate_uuid()
        try:
            if json_string:
                data = json.loads(json_string)
            elif file_path:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
            else:
                return ImportResult(
                    success=False,
                    import_id=import_id,
                    format=ImportFormat.JSON,
                    errors=["No file path or JSON string provided"],
                )

            if not isinstance(data, list):
                data = [data]

            result = ImportResult(
                success=True,
                import_id=import_id,
                format=ImportFormat.JSON,
                records_imported=len(data),
            )
            self._imports[import_id] = result
            return result

        except json.JSONDecodeError as e:
            result = ImportResult(
                success=False,
                import_id=import_id,
                format=ImportFormat.JSON,
                errors=[f"Invalid JSON: {e}"],
            )
            self._imports[import_id] = result
            return result
        except Exception as e:
            result = ImportResult(
                success=False,
                import_id=import_id,
                format=ImportFormat.JSON,
                errors=[str(e)],
            )
            self._imports[import_id] = result
            return result

    def import_csv(
        self,
        file_path: str | None = None,
        csv_string: str | None = None,
        delimiter: str = ",",
    ) -> ImportResult:
        import_id = generate_uuid()
        try:
            if csv_string:
                reader = csv.DictReader(io.StringIO(csv_string), delimiter=delimiter)
                data = list(reader)
            elif file_path:
                with open(file_path, encoding="utf-8") as f:
                    reader = csv.DictReader(f, delimiter=delimiter)
                    data = list(reader)
            else:
                return ImportResult(
                    success=False,
                    import_id=import_id,
                    format=ImportFormat.CSV,
                    errors=["No file path or CSV string provided"],
                )

            result = ImportResult(
                success=True,
                import_id=import_id,
                format=ImportFormat.CSV,
                records_imported=len(data),
            )
            self._imports[import_id] = result
            return result

        except Exception as e:
            result = ImportResult(
                success=False,
                import_id=import_id,
                format=ImportFormat.CSV,
                errors=[str(e)],
            )
            self._imports[import_id] = result
            return result

    def get_import(self, import_id: str) -> ImportResult | None:
        return self._imports.get(import_id)

    def list_imports(self, limit: int = 50) -> list[ImportResult]:
        return sorted(self._imports.values(), key=lambda r: r.import_id, reverse=True)[:limit]

    def get_stats(self) -> dict[str, Any]:
        return {
            "total_imports": len(self._imports),
            "by_format": {fmt.value: sum(1 for r in self._imports.values() if r.format == fmt) for fmt in ImportFormat},
        }


exporter = DataExporter()
importer = DataImporter()
