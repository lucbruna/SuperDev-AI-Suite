from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class Lockfile:
    def __init__(self, lockfile_path: str | Path) -> None:
        self.lockfile_path = Path(lockfile_path)

    def load(self) -> dict[str, str]:
        if not self.lockfile_path.exists():
            return {}
        try:
            with open(self.lockfile_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return {k: str(v) for k, v in data.items()}
            return {}
        except (json.JSONDecodeError, IOError):
            return {}

    def save(self, plugins: dict[str, Any]) -> None:
        data: dict[str, str] = {}
        for name, info in plugins.items():
            if isinstance(info, dict):
                manifest = info.get("manifest", info)
                if isinstance(manifest, dict):
                    version = manifest.get("version", "0.0.0")
                else:
                    version = "0.0.0"
                data[name] = str(version)
            else:
                data[name] = "0.0.0"

        self.lockfile_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.lockfile_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get_version(self, name: str) -> str | None:
        data = self.load()
        return data.get(name)