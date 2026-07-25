"""Streaming utilities for the SuperDev Python SDK."""

from __future__ import annotations

from typing import Any, Callable

from sdk.python.types import StreamingChunk


class StreamProcessor:
    """Processes streaming chunks from the SuperDev API.

    Example::

        processor = StreamProcessor()
        processor.on_chunk(lambda chunk: print(chunk.delta, end=""))
        processor.on_complete(lambda usage: print(f"\\nTokens: {usage}"))
        for chunk in client.chat.stream("Hello"):
            processor.process(chunk)
    """

    def __init__(self) -> None:
        self._on_chunk: Callable[[StreamingChunk], None] | None = None
        self._on_complete: Callable[[dict[str, int]], None] | None = None
        self._on_error: Callable[[Exception], None] | None = None
        self._buffer: list[str] = []
        self._usage: dict[str, int] = {}

    def on_chunk(self, callback: Callable[[StreamingChunk], None]) -> StreamProcessor:
        self._on_chunk = callback
        return self

    def on_complete(self, callback: Callable[[dict[str, int]], None]) -> StreamProcessor:
        self._on_complete = callback
        return self

    def on_error(self, callback: Callable[[Exception], None]) -> StreamProcessor:
        self._on_error = callback
        return self

    def process(self, chunk: StreamingChunk) -> None:
        if chunk.delta:
            self._buffer.append(chunk.delta)
        if chunk.usage:
            self._usage = chunk.usage
        if self._on_chunk:
            self._on_chunk(chunk)
        if chunk.finish_reason and self._on_complete:
            self._on_complete(self._usage)

    @property
    def full_text(self) -> str:
        return "".join(self._buffer)

    @property
    def usage(self) -> dict[str, int]:
        return self._usage

    def reset(self) -> None:
        self._buffer.clear()
        self._usage = {}


class StreamBuffer:
    """Buffers streaming output for reassembly."""

    def __init__(self, max_size: int = 10_000) -> None:
        self._chunks: list[str] = []
        self._max_size = max_size
        self._total_chars = 0

    def add(self, delta: str) -> None:
        if self._total_chars + len(delta) > self._max_size:
            overflow = self._total_chars + len(delta) - self._max_size
            self._chunks = self._chunks[1:] if self._chunks else []
            self._total_chars = max(0, self._total_chars - overflow)
        self._chunks.append(delta)
        self._total_chars += len(delta)

    def get_text(self) -> str:
        return "".join(self._chunks)

    def clear(self) -> None:
        self._chunks.clear()
        self._total_chars = 0

    @property
    def size(self) -> int:
        return self._total_chars
