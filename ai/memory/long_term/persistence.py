from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .storage import Storage


class Persistence:
    """Disk persistence layer for long-term memory."""

    def __init__(self, storage: Storage, base_path: str | Path | None = None):
        self._storage = storage
        self._base_path = Path(base_path) if base_path else Path.cwd() / ".memory_store"

    @property
    def base_path(self) -> Path:
        return self._base_path

    @base_path.setter
    def base_path(self, path: str | Path) -> None:
        self._base_path = Path(path)

    def persist(self, key: str, data: Any) -> None:
        self._base_path.mkdir(parents=True, exist_ok=True)
        path = self._base_path / f"{key}.json"
        path.write_text(json.dumps(data, indent=2) if not isinstance(data, str) else data)

    def load(self, key: str) -> Any | None:
        path = self._base_path / f"{key}.json"
        if not path.exists():
            return None
        try:
            raw = path.read_text()
            data = json.loads(raw) if raw.startswith("{") else raw
            self._storage.put(key, data)
            return data
        except (json.JSONDecodeError, OSError):
            return None

    def exists(self, key: str) -> bool:
        path = self._base_path / f"{key}.json"
        return path.exists()

    def delete(self, key: str) -> bool:
        path = self._base_path / f"{key}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    def list_keys(self) -> list[str]:
        if not self._base_path.exists():
            return []
        return [p.stem for p in self._base_path.glob("*.json")]

    def clear(self) -> None:
        if self._base_path.exists():
            for p in self._base_path.glob("*.json"):
                p.unlink()

    @property
    def count(self) -> int:
        return len(self.list_keys())
