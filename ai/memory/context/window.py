from __future__ import annotations

from typing import Any


class ContextWindow:
    """Sliding window over context data for focused processing."""

    def __init__(self, window_size: int = 100):
        self._window_size = window_size
        self._position: int = 0

    @property
    def window_size(self) -> int:
        return self._window_size

    @window_size.setter
    def window_size(self, value: int) -> None:
        if value < 1:
            raise ValueError("window_size must be >= 1")
        self._window_size = value

    @property
    def position(self) -> int:
        return self._position

    def slice(self, data: list[Any], offset: int | None = None) -> list[Any]:
        start = offset if offset is not None else self._position
        end = start + self._window_size
        return list(data[start:end])

    def advance(self, steps: int = 1) -> None:
        self._position += steps

    def reset(self) -> None:
        self._position = 0

    def window_count(self, total_items: int) -> int:
        if total_items <= 0:
            return 0
        return (total_items + self._window_size - 1) // self._window_size

    def sliding_windows(self, data: list[Any], stride: int = 1) -> list[list[Any]]:
        windows: list[list[Any]] = []
        for i in range(0, len(data) - self._window_size + 1, stride):
            windows.append(list(data[i : i + self._window_size]))
        return windows

    def context_chunks(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        content = context.get("content", {})
        items = list(content.items())
        chunks: list[dict[str, Any]] = []
        for i in range(0, len(items), self._window_size):
            chunk = dict(items[i : i + self._window_size])
            chunks.append({"chunk_index": len(chunks), "content": chunk})
        return chunks
