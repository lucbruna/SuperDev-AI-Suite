from __future__ import annotations

import logging
import re

from ..knowledge_models import DocumentRecord


class PDFProcessor:
    """Parses PDF files to plain text (regex-based fallback without external deps)."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.documents.pdf_processor")

    def can_handle(self, path: str) -> bool:
        return path.lower().endswith(".pdf")

    def parse(self, path: str) -> DocumentRecord:
        try:
            import pypdf  # type: ignore[import-not-found]

            reader = pypdf.PdfReader(path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            text = self._fallback_extract(path)
        return DocumentRecord(
            title=path.rsplit("\\", 1)[-1].rsplit("/", 1)[-1].removesuffix(".pdf"),
            content=text,
            doc_type="pdf",
            metadata={"path": path},
        )

    @staticmethod
    def _fallback_extract(path: str) -> str:
        with open(path, "rb") as handle:
            data = handle.read()
        # crude text extraction: decode latin-1 and strip binary noise
        text = data.decode("latin-1", errors="ignore")
        text = re.sub(r"[^\x20-\x7E\n]", " ", text)
        return "\n".join(line.strip() for line in text.splitlines() if line.strip())
