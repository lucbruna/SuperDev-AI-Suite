from __future__ import annotations

import logging

from ..knowledge_models import DocumentRecord


class SpreadsheetProcessor:
    """Parses spreadsheet files (.csv, .xlsx) into textual content."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.documents.spreadsheet_processor")

    def can_handle(self, path: str) -> bool:
        return path.lower().endswith((".csv", ".xlsx", ".xls"))

    def parse(self, path: str) -> DocumentRecord:
        if path.lower().endswith(".csv"):
            content = self._parse_csv(path)
        else:
            content = self._parse_excel(path)
        return DocumentRecord(
            title=path.rsplit("\\", 1)[-1].rsplit("/", 1)[-1].rsplit(".", 1)[0],
            content=content,
            doc_type="spreadsheet",
            metadata={"path": path},
        )

    @staticmethod
    def _parse_csv(path: str) -> str:
        import csv

        with open(path, newline="", encoding="utf-8", errors="ignore") as handle:
            rows = list(csv.reader(handle))
        return "\n".join(", ".join(cell for cell in row) for row in rows)

    @staticmethod
    def _parse_excel(path: str) -> str:
        try:
            import openpyxl  # type: ignore[import-not-found]

            workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
            lines: list[str] = []
            for sheet in workbook.worksheets:
                lines.append(f"[Sheet: {sheet.title}]")
                for row in sheet.iter_rows(values_only=True):
                    cells = [str(cell) for cell in row if cell is not None]
                    if cells:
                        lines.append(", ".join(cells))
            return "\n".join(lines)
        except ImportError:
            return ""
