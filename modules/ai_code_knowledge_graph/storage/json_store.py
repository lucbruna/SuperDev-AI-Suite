"""JSON file store — one JSON document per key in a directory.

The dependency-free default backend: every payload is written as
``<directory>/<key>.json`` so snapshots and exports are human-readable and
portable between machines.
"""
from __future__ import annotations

import json
import re
import urllib.parse
from pathlib import Path
from typing import Any

from modules.ai_code_knowledge_graph.storage.store import Store

# Keys matching this are stored under their own name (readable files); every
# other key is percent-encoded so round-trips are lossless and Windows-safe
# (e.g. "doc:one" -> "enc_doc%3Aone.json").
_SAFE_KEY = re.compile(r"[A-Za-z0-9._-]+\Z")
_ENCODED_PREFIX = "enc_"


class JsonFileStore:
    """Key/value store backed by JSON files in a single directory."""

    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory)

    def _filename(self, key: str) -> str:
        if _SAFE_KEY.fullmatch(key):
            return key
        return _ENCODED_PREFIX + urllib.parse.quote(key, safe="")

    def _key_from_stem(self, stem: str) -> str:
        if stem.startswith(_ENCODED_PREFIX):
            return urllib.parse.unquote(stem[len(_ENCODED_PREFIX):])
        return stem

    def _path(self, key: str) -> Path:
        return self.directory / f"{self._filename(key)}.json"

    def save(self, key: str, payload: dict[str, Any]) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        self._path(key).write_text(
            json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8"
        )

    def load(self, key: str) -> dict[str, Any] | None:
        path = self._path(key)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def delete(self, key: str) -> bool:
        path = self._path(key)
        if path.exists():
            path.unlink()
            return True
        return False

    def exists(self, key: str) -> bool:
        return self._path(key).exists()

    def list_keys(self, prefix: str = "") -> list[str]:
        if not self.directory.exists():
            return []
        keys = []
        for path in self.directory.glob("*.json"):
            key = self._key_from_stem(path.stem)
            if key.startswith(prefix):
                keys.append(key)
        return sorted(keys)

    def clear(self) -> None:
        if not self.directory.exists():
            return
        for path in self.directory.glob("*.json"):
            path.unlink()
