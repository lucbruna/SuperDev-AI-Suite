from __future__ import annotations

import json
import os
from typing import Any


class FileStorage:
    """File-based storage backend for monitoring data."""

    def __init__(self, directory: str = "monitoring_data") -> None:
        self._directory = directory
        os.makedirs(directory, exist_ok=True)

    def _path(self, key: str) -> str:
        safe = key.replace("/", "_").replace("\\", "_")
        return os.path.join(self._directory, f"{safe}.json")

    def store(self, key: str, data: dict[str, Any]) -> None:
        path = self._path(key)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def retrieve(self, key: str) -> dict[str, Any] | None:
        path = self._path(key)
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def delete(self, key: str) -> bool:
        path = self._path(key)
        try:
            os.remove(path)
            return True
        except FileNotFoundError:
            return False

    def list_keys(self) -> list[str]:
        keys: list[str] = []
        for fname in os.listdir(self._directory):
            if fname.endswith(".json"):
                keys.append(fname[:-5])
        return keys

    def close(self) -> None:
        pass
