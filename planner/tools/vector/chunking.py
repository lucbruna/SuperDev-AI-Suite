from __future__ import annotations

from typing import Any


class Chunking:
    """Document chunking strategies."""

    @staticmethod
    def fixed_size(text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks

    @staticmethod
    def paragraph(text: str) -> list[str]:
        return [p.strip() for p in text.split("\n\n") if p.strip()]

    @staticmethod
    def sentence(text: str) -> list[str]:
        import re
        return [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
