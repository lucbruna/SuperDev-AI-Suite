"""Document metadata extraction (titles, dates, authors, tags)."""

from __future__ import annotations

import re
from typing import Any

from enterprise_knowledge.knowledge_protocols import tokenize


class MetadataExtractor:
    """Infers lightweight metadata from document content."""

    def __init__(self, stopwords: set[str] | None = None) -> None:
        self.stopwords = stopwords or {
            "de", "da", "do", "e", "o", "a", "os", "as", "um", "uma",
            "em", "com", "para", "por", "que", "ao", "no", "na",
        }

    def extract(self, content: str, title: str = "",
                source: str = "") -> dict[str, Any]:
        metadata = {
            "title": title or self._infer_title(content),
            "language": self._detect_language(content),
            "word_count": len(tokenize(content)),
            "characters": len(content),
            "has_dates": bool(re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
                                        content)),
            "has_emails": bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+",
                                         content)),
            "has_urls": bool(re.search(r"https?://", content)),
        }
        tags = self.keywords(content, limit=5)
        if tags:
            metadata["tags"] = tags
        if source:
            metadata["source"] = source
        return metadata

    @staticmethod
    def _infer_title(content: str) -> str:
        for line in (content or "").splitlines():
            stripped = line.strip()
            if stripped and len(stripped) < 80:
                return stripped
        return ""

    @staticmethod
    def _detect_language(content: str) -> str:
        pt = {"não", "com", "para", "que", "uma", "dos", "das"}
        en = {"the", "with", "and", "for", "from", "this"}
        words = set(tokenize(content.lower()))
        if len(words & pt) > len(words & en):
            return "pt-BR"
        return "en" if words & en else "unknown"

    def keywords(self, content: str, limit: int = 5) -> list[str]:
        counts: dict[str, int] = {}
        for token in tokenize(content.lower()):
            if len(token) < 3 or token in self.stopwords:
                continue
            counts[token] = counts.get(token, 0) + 1
        ranked = sorted(counts, key=lambda token: counts[token],  # type: ignore[arg-type]
                        reverse=True)
        return ranked[:limit]
