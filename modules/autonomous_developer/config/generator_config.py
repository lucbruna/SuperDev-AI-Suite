"""Generator configuration — code generation constraints and safety.

Environment prefix: ``SUPERDEV_AD_GENERATOR_*``.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from modules.autonomous_developer.config.constants import RISK_CRITICAL


def _env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(key: str, default: int) -> int:
    raw = os.getenv(key)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


@dataclass(slots=True)
class GeneratorConfig:
    """Constraints the code generator must respect."""

    max_file_size_bytes: int = 256_000
    max_files_per_task: int = 50
    max_changed_lines_per_task: int = 2_000
    indent: int = 4
    line_length: int = 100
    encoding: str = "utf-8"
    newline: str = "\n"

    # Write safety.
    create_backups: bool = True
    atomic_writes: bool = True
    allow_new_files: bool = True
    allow_modify_existing: bool = True
    allow_delete: bool = False

    # Generation behaviour.
    use_coding_rules: bool = True
    use_style_rules: bool = True
    max_retries_on_lint_failure: int = 2

    # Risk policy: plans with any task above this risk level are blocked
    # (low < medium < high < critical).
    max_risk_level: str = RISK_CRITICAL

    @classmethod
    def from_env(cls) -> GeneratorConfig:
        cfg = cls()
        cfg.max_files_per_task = _env_int(
            "SUPERDEV_AD_GENERATOR_MAX_FILES", cfg.max_files_per_task
        )
        cfg.line_length = _env_int("SUPERDEV_AD_GENERATOR_LINE_LENGTH", cfg.line_length)
        cfg.allow_delete = _env_bool("SUPERDEV_AD_GENERATOR_ALLOW_DELETE", cfg.allow_delete)
        cfg.create_backups = _env_bool(
            "SUPERDEV_AD_GENERATOR_BACKUPS", cfg.create_backups
        )
        cfg.atomic_writes = _env_bool(
            "SUPERDEV_AD_GENERATOR_ATOMIC", cfg.atomic_writes
        )
        cfg.max_risk_level = os.getenv(
            "SUPERDEV_AD_GENERATOR_MAX_RISK", cfg.max_risk_level
        ).strip() or cfg.max_risk_level
        return cfg
