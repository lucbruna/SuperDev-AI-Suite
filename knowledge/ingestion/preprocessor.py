from __future__ import annotations

import logging
import re


class Preprocessor:
    """Normalizes and cleans text before chunking and embedding."""

    def __init__(self, collapse_whitespace: bool = True, strip_markdown: bool = False) -> None:
        self._log = logging.getLogger("superdev.knowledge.ingestion.preprocessor")
        self._collapse_whitespace = collapse_whitespace
        self._strip_markdown = strip_markdown

    def clean(self, text: str) -> str:
        cleaned = text or ""
        if self._strip_markdown:
            cleaned = re.sub(r"[#>*_`~\[\]()!-]", " ", cleaned)
        if self._collapse_whitespace:
            cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip()

    def normalize(self, text: str, lowercase: bool = True) -> str:
        normalized = self.clean(text)
        if lowercase:
            normalized = normalized.lower()
        return normalized

    def truncate(self, text: str, max_chars: int) -> str:
        if not text or len(text) <= max_chars:
            return text or ""
        return text[:max_chars]
