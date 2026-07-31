"""Lake compression helpers."""

from __future__ import annotations

import gzip
import json
from typing import Any


class Compressor:
    """Gzip + JSON helpers for lake objects."""

    @staticmethod
    def dumps(records: list[dict[str, Any]]) -> bytes:
        return gzip.compress(json.dumps(records).encode("utf-8"))

    @staticmethod
    def loads(blob: bytes) -> list[dict[str, Any]]:
        return json.loads(gzip.decompress(blob).decode("utf-8"))

    @staticmethod
    def ratio(raw: bytes, compressed: bytes) -> float:
        """Compression ratio (1.0 = no gain)."""
        if not raw:
            return 0.0
        return round(len(compressed) / len(raw), 4)
