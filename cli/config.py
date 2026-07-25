import os
from pathlib import Path
from typing import Any

import yaml


class CLIConfig:
    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path or Path.home() / ".superdev" / "config.yaml"
        self._data: dict[str, Any] = {}
        self._load()

    def _load(self):
        if self.config_path.exists():
            with open(self.config_path) as f:
                self._data = yaml.safe_load(f) or {}
        else:
            self._data = self._defaults()
            self._save()

    def _defaults(self) -> dict[str, Any]:
        return {
            "api_url": os.getenv("SUPERDEV_API_URL", "http://localhost:8000"),
            "environment": os.getenv("SUPERDEV_ENV", "development"),
            "theme": "dark",
            "editor": {"font_size": 14, "tab_size": 4, "word_wrap": True},
            "terminal": {"shell": "bash", "font_size": 13},
            "providers": {},
        }

    def _save(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            yaml.dump(self._data, f, default_flow_style=False)

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self._data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def set(self, key: str, value: Any):
        keys = key.split(".")
        target = self._data
        for k in keys[:-1]:
            target = target.setdefault(k, {})
        target[keys[-1]] = value
        self._save()

    @property
    def api_url(self) -> str:
        return self.get("api_url")

    @property
    def environment(self) -> str:
        return self.get("environment")

    @property
    def theme(self) -> str:
        return self.get("theme")