from __future__ import annotations

import logging

from ..knowledge_models import DocumentRecord


class WordProcessor:
    """Parses .docx files to plain text."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.documents.word_processor")

    def can_handle(self, path: str) -> bool:
        return path.lower().endswith((".docx", ".doc"))

    def parse(self, path: str) -> DocumentRecord:
        text = ""
        try:
            from docx import Document  # type: ignore[import-notified]

            document = Document(path)
            text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        except ImportError:
            text = self._fallback(path)
        return DocumentRecord(
            title=path.rsplit("\\", 1)[-1].rsplit("/", 1)[-1].rsplit(".", 1)[0],
            content=text,
            doc_type="word",
            metadata={"path": path},
        )

    @staticmethod
    def _fallback(path: str) -> str:
        try:
            with open(path, "rb") as handle:
                data = handle.read()
            # .docx is a zip; try reading word/document.xml
            if data[:2] == b"PK":
                import re
                import zipfile
                import io

                with zipfile.ZipFile(io.BytesIO(data)) as archive:
                    xml = archive.read("word/document.xml").decode("utf-8", errors="ignore")
                xml = re.sub(r"<w:p[^>]*>", "\n", xml)
                xml = re.sub(r"<[^>]+>", "", xml)
                return xml
        except (OSError, KeyError):  # noqa: BLE001
            pass
        return ""
