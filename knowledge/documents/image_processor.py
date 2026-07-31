from __future__ import annotations

import logging

from ..knowledge_models import DocumentRecord


class ImageProcessor:
    """Extracts textual content from images (OCR optional; falls back to metadata)."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.documents.image_processor")

    def can_handle(self, path: str) -> bool:
        return path.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"))

    def parse(self, path: str) -> DocumentRecord:
        text = ""
        try:
            import pytesseract  # type: ignore[import-not-found]
            from PIL import Image  # type: ignore[import-not-found]

            text = pytesseract.image_to_string(Image.open(path))
        except ImportError:
            text = "[image content requires OCR support]"
        return DocumentRecord(
            title=path.rsplit("\\", 1)[-1].rsplit("/", 1)[-1],
            content=text,
            doc_type="image",
            metadata={"path": path},
        )
