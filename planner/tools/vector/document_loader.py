from __future__ import annotations

import csv
import json
from typing import Any


class DocumentLoader:
    """Load documents from various file formats."""

    @staticmethod
    def load_text(path: str) -> str:
        with open(path, encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def load_json(path: str) -> dict[str, Any]:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_json_lines(path: str) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records

    @staticmethod
    def load_csv(path: str, **kwargs: Any) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, **kwargs)
            for row in reader:
                rows.append(row)
        return rows

    @staticmethod
    def load_pdf(path: str) -> str:
        """Extract text from a PDF file (stub — requires PyMuPDF or similar)."""
        raise NotImplementedError("PDF loading requires an external library like PyMuPDF")
