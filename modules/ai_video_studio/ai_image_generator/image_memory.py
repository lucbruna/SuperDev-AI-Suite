"""Image memory — recall past image generation requests."""
from __future__ import annotations

import time
from typing import Any


class ImageMemory:
    """Bounded memory of image generation requests."""

    def __init__(self, max_entries: int = 500) -> None:
        self.max_entries = max_entries
        self._entries: list[dict[str, Any]] = []

    def remember(self, *, prompt: str, style: str, output_ref: str) -> None:
        self._entries.append(
            {"prompt": prompt, "style": style, "output_ref": output_ref, "timestamp": time.time()}
        )
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries :]

    def recent(self, limit: int = 10) -> list[dict[str, Any]]:
        return list(self._entries[-limit:])

    def count(self) -> int:
        return len(self._entries)


_image_memory: ImageMemory | None = None


def get_image_memory() -> ImageMemory:
    global _image_memory
    if _image_memory is None:
        _image_memory = ImageMemory()
    return _image_memory
