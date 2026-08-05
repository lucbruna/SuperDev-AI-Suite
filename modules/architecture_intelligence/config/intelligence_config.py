"""Configuration model for the Architecture Intelligence module.

Uses plain dataclasses + environment overrides (``SUPERDEV_INTELLIGENCE_<KEY>``)
so the module has no hard dependencies beyond the standard library.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

DATA_DIR_NAME = ".superdev"
INTELLIGENCE_DIR = "architecture_intelligence"
HISTORY_FILE = "history.json"
DEFAULT_LLM_PROVIDER = "auto"  # auto | openai | anthropic | local | none
DEFAULT_LLM_MODEL = ""


def _env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class IntelligenceConfig:
    """Runtime configuration for the intelligence engine."""

    project_root: str = ""
    enabled: bool = True

    # History / storage
    data_dir: str = ""
    history_file: str = HISTORY_FILE
    history_limit: int = 500       # max snapshots retained
    history_min_interval_seconds: int = 300  # min time between snapshots

    # LLM provider (graceful degradation when unset)
    llm_provider: str = DEFAULT_LLM_PROVIDER
    llm_model: str = DEFAULT_LLM_MODEL
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_timeout_seconds: int = 30

    # Agents
    agents_enabled: bool = True
    agent_max_steps: int = 5

    # Scheduler
    scheduler_enabled: bool = True
    schedule_interval_minutes: int = 60

    # Analysis toggles
    forecast_horizon: int = 5      # weeks of trend projection
    max_insights: int = 10

    @classmethod
    def from_env(cls) -> "IntelligenceConfig":
        cfg = cls()
        cfg.enabled = _env_bool("SUPERDEV_INTELLIGENCE_ENABLED", cfg.enabled)
        cfg.llm_provider = os.getenv("SUPERDEV_INTELLIGENCE_LLM_PROVIDER", cfg.llm_provider)
        cfg.llm_model = os.getenv("SUPERDEV_INTELLIGENCE_LLM_MODEL", cfg.llm_model)
        cfg.llm_api_key = os.getenv("SUPERDEV_INTELLIGENCE_LLM_API_KEY", cfg.llm_api_key)
        cfg.llm_base_url = os.getenv("SUPERDEV_INTELLIGENCE_LLM_BASE_URL", cfg.llm_base_url)
        cfg.agents_enabled = _env_bool("SUPERDEV_INTELLIGENCE_AGENTS", cfg.agents_enabled)
        cfg.scheduler_enabled = _env_bool(
            "SUPERDEV_INTELLIGENCE_SCHEDULER", cfg.scheduler_enabled
        )
        cfg.schedule_interval_minutes = int(
            os.getenv("SUPERDEV_INTELLIGENCE_INTERVAL_MINUTES", str(cfg.schedule_interval_minutes))
        )
        cfg.forecast_horizon = int(
            os.getenv("SUPERDEV_INTELLIGENCE_FORECAST_WEEKS", str(cfg.forecast_horizon))
        )
        return cfg

    def resolve(self, project_root: str | None = None) -> None:
        """Resolve project root and derived paths."""
        if project_root:
            self.project_root = str(Path(project_root).resolve())
        if not self.project_root:
            self.project_root = str(
                Path(__file__).resolve().parent.parent.parent.parent
            )
        if not self.data_dir:
            self.data_dir = str(
                Path(self.project_root) / DATA_DIR_NAME / INTELLIGENCE_DIR
            )

    @property
    def history_path(self) -> str:
        return str(Path(self.data_dir) / self.history_file)
