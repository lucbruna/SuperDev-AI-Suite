"""Scanner configuration — filesystem walking and per-language scanning.

Controls which directories/files are scanned, safety caps and scan
behaviour. Environment prefix: ``SUPERDEV_KG_SCAN_*``.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from modules.ai_code_knowledge_graph.config.constants import (
    FRONTEND_DIRS,
    IGNORE_DIRS,
    IGNORE_FILES,
    PROJECT_DIRS,
)


def _env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class ScannerConfig:
    """Runtime configuration for repository scanning."""

    project_root: str = ""
    project_dirs: tuple[str, ...] = PROJECT_DIRS
    frontend_dirs: tuple[str, ...] = FRONTEND_DIRS
    ignore_dirs: frozenset[str] = IGNORE_DIRS
    ignore_files: frozenset[str] = IGNORE_FILES
    language_extensions: dict[str, str] | None = None

    scan_frontend: bool = True
    max_files: int = 20000
    max_file_size: int = 1_500_000
    follow_symlinks: bool = False
    include_hidden: bool = False
    max_line_length: int = 1000
    read_binary_as_text: bool = False

    @classmethod
    def from_env(cls) -> "ScannerConfig":
        cfg = cls()
        cfg.scan_frontend = _env_bool("SUPERDEV_KG_SCAN_FRONTEND", cfg.scan_frontend)
        cfg.max_files = int(os.getenv("SUPERDEV_KG_SCAN_MAX_FILES", str(cfg.max_files)))
        cfg.max_file_size = int(os.getenv("SUPERDEV_KG_SCAN_MAX_FILE_SIZE", str(cfg.max_file_size)))
        cfg.follow_symlinks = _env_bool("SUPERDEV_KG_SCAN_SYMLINKS", cfg.follow_symlinks)
        cfg.include_hidden = _env_bool("SUPERDEV_KG_SCAN_HIDDEN", cfg.include_hidden)
        return cfg

    @property
    def scan_dirs(self) -> tuple[str, ...]:
        dirs = list(self.project_dirs)
        if self.scan_frontend:
            dirs.extend(self.frontend_dirs)
        return tuple(dirs)

    def resolve(self, project_root: str | None = None) -> None:
        if project_root:
            self.project_root = project_root
        if not self.project_root:
            self.project_root = str(
                __import__("pathlib").Path(__file__).resolve().parent.parent.parent.parent
            )
