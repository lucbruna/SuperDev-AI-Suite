from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


class DevOpsConfig:
    """Configuration manager for DevOps operations."""

    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or Path.cwd() / "devops.yaml"
        self._data: dict[str, Any] = self._defaults()
        self._load()

    def _defaults(self) -> dict[str, Any]:
        return {
            "environment": os.getenv("DEVOPS_ENV", "development"),
            "provider": os.getenv("DEVOPS_PROVIDER", "local"),
            "region": os.getenv("DEVOPS_REGION", "us-east-1"),
            "namespace": os.getenv("DEVOPS_NAMESPACE", "default"),
            "docker": {"registry": "docker.io", "tag": "latest"},
            "kubernetes": {"namespace": "default", "replicas": 1},
            "cicd": {"pipeline": "github_actions"},
            "monitoring": {"enabled": True, "interval": 30},
        }

    def _load(self) -> None:
        if self.config_path and self.config_path.exists():
            with self.config_path.open() as f:
                loaded = yaml.safe_load(f) or {}
                self._data.update(loaded)

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self._data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def set(self, key: str, value: Any) -> None:
        keys = key.split(".")
        target = self._data
        for k in keys[:-1]:
            target = target.setdefault(k, {})
        target[keys[-1]] = value

    @property
    def environment(self) -> str:
        return self.get("environment")

    @property
    def provider(self) -> str:
        return self.get("provider")

    @property
    def region(self) -> str:
        return self.get("region")
