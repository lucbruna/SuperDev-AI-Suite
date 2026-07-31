"""Base classes for the data lake."""

from __future__ import annotations

import json
import zlib
from pathlib import Path
from typing import Any, Iterable


class LakeError(Exception):
    """Raised on data lake operation failures."""


class LakeZone:
    """A zone in the lake (raw, cleansed, curated)."""

    def __init__(self, name: str, root: str | Path = "") -> None:
        self.name = name
        self.root = Path(root) if root else Path(f"lake/{name}")
        self._objects: dict[str, dict[str, Any]] = {}

    def put(self, key: str, data: Any,
            compress: bool = False) -> dict[str, Any]:
        """Stores an object under ``key`` (optionally compressed JSON)."""
        if compress:
            raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
            blob = zlib.compress(raw)
            meta = {"compressed": True, "bytes": len(blob),
                    "type": "application/zlib+json"}
        else:
            blob = json.dumps(data, ensure_ascii=False).encode("utf-8")
            meta = {"compressed": False, "bytes": len(blob),
                    "type": "application/json"}
        self._objects[key] = {"data": blob, "meta": meta}
        self._flush(key, blob)
        return meta

    def get(self, key: str) -> Any:
        """Returns the object decoded as JSON."""
        entry = self._objects.get(key)
        if entry is None:
            raise LakeError(f"object not found: {key}")
        blob = entry["data"]
        if entry["meta"].get("compressed"):
            blob = zlib.decompress(blob)
        return json.loads(blob.decode("utf-8"))

    def keys(self) -> list[str]:
        return list(self._objects)

    def exists(self, key: str) -> bool:
        return key in self._objects

    def delete(self, key: str) -> bool:
        return self._objects.pop(key, None) is not None

    def size(self) -> int:
        return len(self._objects)

    def _flush(self, key: str, blob: bytes) -> None:
        """Persists the object to disk (no-op unless a root is set)."""
        if self.root != Path("lake/raw") or not self.root.exists():
            self.root.mkdir(parents=True, exist_ok=True)
        target = self.root / f"{key.replace('/', '_')}.json"
        target.write_bytes(blob)
