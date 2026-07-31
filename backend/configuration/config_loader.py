from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConfigLoader:
    """Configuration file loader."""

    def __init__(self, config_dir: str = "config"):
        self._config_dir = Path(config_dir)
        self._config: dict[str, Any] = {}

    def load_json(self, filename: str) -> dict[str, Any]:
        path = self._config_dir / filename
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return {}

    def load_yaml(self, filename: str) -> dict[str, Any]:
        try:
            import yaml

            path = self._config_dir / filename
            if path.exists():
                with open(path) as f:
                    return yaml.safe_load(f) or {}
        except ImportError:
            pass
        return {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._config[key] = value

    def update(self, data: dict[str, Any]) -> None:
        self._config.update(data)


config_loader = ConfigLoader()
