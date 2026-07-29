from __future__ import annotations

import re
from typing import Any

FORMAT_HANDLERS: dict[str, str] = {
    "txt": "text/plain",
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "html": "text/html",
    "md": "text/markdown",
    "json": "application/json",
}


class DocumentParser:
    async def parse(self, content: str, format: str = "txt") -> dict[str, Any]:
        fmt = format.lower().strip(".")
        if fmt not in FORMAT_HANDLERS:
            raise ValueError(f"Unsupported format: '{format}'. Supported: {', '.join(FORMAT_HANDLERS)}")

        sections = await self.extract_sections(content, fmt)
        lang = await self.detect_language(content)
        normalized = await self.normalize_content(content)

        return {
            "format": fmt,
            "mime_type": FORMAT_HANDLERS[fmt],
            "content": normalized,
            "sections": sections,
            "language": lang,
            "length": len(normalized),
            "word_count": len(normalized.split()),
        }

    async def parse_by_type(self, content: str, mime_type: str) -> dict[str, Any]:
        reverse_map = {v: k for k, v in FORMAT_HANDLERS.items()}
        fmt = reverse_map.get(mime_type)
        if fmt is None:
            raise ValueError(f"Unsupported mime type: '{mime_type}'")
        return await self.parse(content, fmt)

    async def extract_sections(self, content: str, format: str) -> list[dict[str, Any]]:
        sections = []
        lines = content.split("\n")
        current_section: dict[str, Any] | None = None

        for i, line in enumerate(lines):
            stripped = line.strip()
            if format == "md" and stripped.startswith("#"):
                level = len(re.match(r"^#+", stripped).group())
                if current_section:
                    sections.append(current_section)
                current_section = {"level": level, "title": stripped.lstrip("#").strip(), "start_line": i + 1, "content_lines": 0}
            elif format == "html" and re.match(r"<h[1-6]>", stripped, re.IGNORECASE):
                if current_section:
                    sections.append(current_section)
                title = re.sub(r"<[^>]+>", "", stripped).strip()
                current_section = {"level": int(stripped[2]), "title": title, "start_line": i + 1, "content_lines": 0}
            elif current_section is not None and stripped:
                current_section["content_lines"] = current_section.get("content_lines", 0) + 1

        if current_section:
            sections.append(current_section)

        if not sections:
            sections = [{"level": 1, "title": "Body", "start_line": 1, "content_lines": len([l for l in lines if l.strip()])}]

        return sections

    async def detect_language(self, content: str) -> str:
        en_indicators = ["the", "and", "is", "are", "was", "were", "have", "has", "been", "will"]
        tokens = content.lower().split()
        en_count = sum(1 for t in tokens if t in en_indicators)
        if len(tokens) == 0:
            return "unknown"
        ratio = en_count / len(tokens)
        if ratio > 0.05:
            return "en"
        if any(ord(c) > 0x4E00 for c in content[:100]):
            return "zh"
        return "unknown"

    async def normalize_content(self, content: str) -> str:
        normalized = re.sub(r"\s+", " ", content).strip()
        return normalized