from __future__ import annotations

import json
import zlib
from typing import Any


class Compression:
    """Compression utilities for long-term memory data."""

    def __init__(self, level: int = 6):
        self._level = level

    @property
    def level(self) -> int:
        return self._level

    def compress(self, data: dict[str, Any]) -> bytes:
        raw = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
        return zlib.compress(raw, level=self._level)

    def decompress(self, data: bytes) -> dict[str, Any]:
        raw = zlib.decompress(data)
        return json.loads(raw.decode("utf-8"))

    def compress_string(self, text: str) -> bytes:
        return zlib.compress(text.encode("utf-8"), level=self._level)

    def decompress_string(self, data: bytes) -> str:
        return zlib.decompress(data).decode("utf-8")

    def ratio(self, original: dict[str, Any], compressed: bytes) -> float:
        raw_size = len(json.dumps(original, sort_keys=True, default=str).encode("utf-8"))
        if raw_size == 0:
            return 0.0
        return 1.0 - (len(compressed) / raw_size)
