from __future__ import annotations

import zlib
from typing import Any, Dict


class Compression:
    """Compresses message data."""

    @staticmethod
    def compress(data: str) -> bytes:
        return zlib.compress(data.encode())

    @staticmethod
    def decompress(data: bytes) -> str:
        return zlib.decompress(data).decode()

    @staticmethod
    def compress_dict(data: Dict[str, Any]) -> bytes:
        import json
        return zlib.compress(json.dumps(data, default=str).encode())

    @staticmethod
    def decompress_dict(data: bytes) -> Dict[str, Any]:
        import json
        return json.loads(zlib.decompress(data).decode())
