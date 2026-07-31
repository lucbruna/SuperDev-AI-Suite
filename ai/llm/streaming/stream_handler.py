from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import Any


class StreamHandler:
    """Accumulates streaming chunks into a complete response."""

    def __init__(self) -> None:
        self._chunks: list[dict[str, Any]] = []
        self._complete_content: list[str] = []

    async def collect(self, stream: AsyncIterator[dict[str, Any]]) -> dict[str, Any]:
        self._chunks.clear()
        self._complete_content.clear()

        async for chunk in stream:
            self._chunks.append(chunk)
            content = chunk.get("content", "")
            if isinstance(content, str):
                self._complete_content.append(content)
            if chunk.get("finish_reason") == "stop":
                break

        full_content = "".join(self._complete_content)
        last_chunk = self._chunks[-1] if self._chunks else {}

        return {
            "content": full_content,
            "success": True,
            "chunk_count": len(self._chunks),
            "finish_reason": last_chunk.get("finish_reason", "stop"),
            "tokens_prompt": sum(c.get("tokens_prompt", 0) for c in self._chunks),
            "tokens_completion": sum(c.get("tokens_completion", 0) for c in self._chunks),
        }

    async def process(
        self,
        stream: AsyncIterator[dict[str, Any]],
        on_chunk: Callable[[dict[str, Any]], Any] | None = None,
    ) -> dict[str, Any]:
        async for chunk in stream:
            self._chunks.append(chunk)
            content = chunk.get("content", "")
            if isinstance(content, str):
                self._complete_content.append(content)
            if on_chunk:
                on_chunk(chunk)
            if chunk.get("finish_reason") == "stop":
                break

        full_content = "".join(self._complete_content)
        last_chunk = self._chunks[-1] if self._chunks else {}
        return {
            "content": full_content,
            "success": True,
            "chunk_count": len(self._chunks),
            "finish_reason": last_chunk.get("finish_reason", "stop"),
        }

    @property
    def chunk_count(self) -> int:
        return len(self._chunks)

    @property
    def full_content(self) -> str:
        return "".join(self._complete_content)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_count": self.chunk_count,
            "content_length": len(self.full_content),
        }
