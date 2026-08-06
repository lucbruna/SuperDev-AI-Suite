"""Top-level Autonomous Developer configuration.

Environment prefix: ``SUPERDEV_AD_*``.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from modules.autonomous_developer.config.constants import (
    DATA_DIR_NAME,
    DEFAULT_WORK_BRANCH,
    MODE_SUPERVISED,
    MODULE_DATA_DIR,
)
from modules.autonomous_developer.config.generator_config import GeneratorConfig
from modules.autonomous_developer.config.llm_config import LLMConfig
from modules.autonomous_developer.config.planner_config import PlannerConfig


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
class DeveloperConfig:
    """Top-level configuration for the Autonomous Developer runtime."""

    name: str = "autonomous_developer"
    version: int = 1

    # How the developer behaves.
    mode: str = MODE_SUPERVISED  # autonomous | supervised | review_only
    work_branch: str = DEFAULT_WORK_BRANCH
    allow_main_branch_writes: bool = False
    max_retries_per_task: int = 3
    max_concurrent_tasks: int = 2

    # Sub-configs.
    planner: PlannerConfig = field(default_factory=PlannerConfig)
    generator: GeneratorConfig = field(default_factory=GeneratorConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)

    # Pipeline gates.
    run_tests: bool = True
    run_lint: bool = True
    run_review: bool = True
    run_docs: bool = True
    create_pr: bool = True

    # Storage.
    project_root: str = ""
    data_dir: str = ""
    db_file: str = "autonomous_developer.db"
    session_file: str = "sessions.json"
    log_dir: str = "logs"
    reports_dir: str = "reports"
    artifacts_dir: str = "artifacts"

    # Persistence.
    autosave_session: bool = True
    max_sessions: int = 50

    @classmethod
    def from_env(cls) -> DeveloperConfig:
        cfg = cls()
        cfg.planner = PlannerConfig.from_env()
        cfg.generator = GeneratorConfig.from_env()
        cfg.llm = LLMConfig.from_env()
        cfg.mode = os.getenv("SUPERDEV_AD_MODE", cfg.mode)
        cfg.work_branch = os.getenv("SUPERDEV_AD_WORK_BRANCH", cfg.work_branch)
        cfg.allow_main_branch_writes = _env_bool(
            "SUPERDEV_AD_ALLOW_MAIN_WRITES", cfg.allow_main_branch_writes
        )
        cfg.max_retries_per_task = _env_int(
            "SUPERDEV_AD_MAX_RETRIES", cfg.max_retries_per_task
        )
        cfg.run_tests = _env_bool("SUPERDEV_AD_RUN_TESTS", cfg.run_tests)
        cfg.run_lint = _env_bool("SUPERDEV_AD_RUN_LINT", cfg.run_lint)
        cfg.run_review = _env_bool("SUPERDEV_AD_RUN_REVIEW", cfg.run_review)
        cfg.create_pr = _env_bool("SUPERDEV_AD_CREATE_PR", cfg.create_pr)
        return cfg

    def resolve(self, project_root: str | None = None) -> None:
        """Resolve project root and derived data paths.

        Honors an explicitly configured ``project_root``; falls back to the
        current working directory when none was set.
        """
        import pathlib

        if project_root:
            root = pathlib.Path(project_root).resolve()
        elif self.project_root:
            root = pathlib.Path(self.project_root).resolve()
        else:
            root = pathlib.Path.cwd().resolve()
        self.project_root = str(root)
        if not self.data_dir:
            self.data_dir = str(root / DATA_DIR_NAME / MODULE_DATA_DIR)
