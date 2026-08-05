"""Process-wide settings singleton for the Architecture Graph module."""
from __future__ import annotations

import threading
from pathlib import Path
from typing import Any

from modules.architecture_graph.config.graph_config import GraphConfig


class GraphSettings:
    """Thread-safe singleton holding the resolved :class:`GraphConfig`."""

    _instance: "GraphSettings | None" = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self.config = GraphConfig.from_env()
        self.config.resolve()
        self._mutable: dict[str, Any] = {}

    # -- Singleton ---------------------------------------------------------
    @classmethod
    def instance(cls) -> "GraphSettings":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    # -- Derived helpers ---------------------------------------------------
    @property
    def data_dir(self) -> Path:
        return Path(self.config.data_dir)

    @property
    def db_path(self) -> Path:
        return Path(self.config.db_path)

    @property
    def export_dir(self) -> Path:
        return Path(self.config.export_path)

    @property
    def project_root(self) -> Path:
        return Path(self.config.project_root)

    def ensure_dirs(self) -> None:
        """Create the directories the module persists into."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    # -- Mutable scratch state --------------------------------------------
    def set(self, key: str, value: Any) -> None:
        self._mutable[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._mutable.get(key, default)


def get_settings() -> GraphSettings:
    """Return the module-wide settings singleton (configures on first use)."""
    settings = GraphSettings.instance()
    settings.ensure_dirs()
    return settings
