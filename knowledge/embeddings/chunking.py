from __future__ import annotations

import logging
from typing import Any

from ..knowledge_interfaces import Chunker
from ..knowledge_models import Chunk


class SlidingWindowChunker(Chunker):
    """Splits text into fixed-size chunks with configurable overlap."""

    def __init__(self, chunk_size: int = 512, overlap: int = 64) -> None:
        self._log = logging.getLogger("superdev.knowledge.embeddings.chunking")
        self._chunk_size = max(1, chunk_size)
        self._overlap = max(0, min(overlap, self._chunk_size // 2))

    def chunk(self, text: str, document_id: str = "") -> list[Chunk]:
        step = self._chunk_size - self._overlap
        chunks: list[Chunk] = []
        for i, start in enumerate(range(0, len(text), step)):
            piece = text[start:start + self._chunk_size]
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        document_id=document_id,
                        index=i,
                        metadata={"start": start, "end": start + len(piece)},
                    )
                )
            if start + self._chunk_size >= len(text):
                break
        return chunks


class SentenceChunker(Chunker):
    """Splits text into sentence-aligned chunks below a maximum size."""

    def __init__(self, max_size: int = 512) -> None:
        self._log = logging.getLogger("superdev.knowledge.embeddings.sentence_chunker")
        self._max_size = max_size

    def chunk(self, text: str, document_id: str = "") -> list[Chunk]:
        sentences = [s.strip() for s in text.replace("\n", " ").split(". ") if s.strip()]
        chunks: list[Chunk] = []
        current = ""
        index = 0
        for sentence in sentences:
            candidate = (current + " " + sentence).strip() if current else sentence
            if len(candidate) > self._max_size and current:
                chunks.append(Chunk(text=current, document_id=document_id, index=index))
                index += 1
                current = sentence
            else:
                current = candidate
        if current:
            chunks.append(Chunk(text=current, document_id=document_id, index=index))
        return chunks
