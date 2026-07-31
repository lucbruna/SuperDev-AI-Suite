from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ..knowledge_models import DocumentRecord
from .pdf_processor import PDFProcessor
from .spreadsheet_processor import SpreadsheetProcessor
from .word_processor import WordProcessor


class Parser:
    """Routes files to the correct format processor."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.documents.parser")
        self._processors = [
            PDFProcessor(),
            WordProcessor(),
            SpreadsheetProcessor(),
        ]

    def parse(self, path: str | Path) -> DocumentRecord:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(str(path))
        for processor in self._processors:
            if processor.can_handle(str(path)):
                return processor.parse(str(path))
        # Fallback: plain text
        return DocumentRecord(
            title=path.stem,
            content=path.read_text(encoding="utf-8", errors="ignore"),
            doc_type="text",
            metadata={"path": str(path)},
        )

    def register(self, processor: Any) -> None:
        self._processors.append(processor)
