from __future__ import annotations

from typing import Any


class Splitter:
    """Document splitting strategies for chunking."""

    @staticmethod
    def recursive_character_split(
        text: str,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        separators: list[str] | None = None,
    ) -> list[str]:
        if separators is None:
            separators = ["\n\n", "\n", ".", " ", ""]
        chunks: list[str] = []
        current = text
        for sep in separators:
            if sep == "":
                for i in range(0, len(current), chunk_size - chunk_overlap):
                    chunks.append(current[i : i + chunk_size])
                break
            parts = current.split(sep)
            buffer = ""
            for part in parts:
                if len(buffer) + len(part) + len(sep) <= chunk_size:
                    buffer = (buffer + sep + part).strip()
                else:
                    if buffer:
                        chunks.append(buffer)
                    buffer = part
            if buffer:
                chunks.append(buffer)
            if len(chunks) > 1:
                break
        return chunks or [text]

    @staticmethod
    def semantic_split(text: str, max_chars: int = 512) -> list[str]:
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks: list[str] = []
        buffer = ""
        for para in paragraphs:
            if len(buffer) + len(para) + 2 <= max_chars:
                buffer = (buffer + "\n\n" + para).strip()
            else:
                if buffer:
                    chunks.append(buffer)
                buffer = para
        if buffer:
            chunks.append(buffer)
        return chunks
