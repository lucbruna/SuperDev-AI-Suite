"""Main configuration for the Self-Healing Engine module."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from modules.self_healing_engine.config._env import (
    env_bool,
    env_int,
    env_str,
)
from modules.self_healing_engine.config.automation_config import AutomationConfig
from modules.self_healing_engine.config.constants import (
    DATA_DIR_NAME,
    DEFAULT_DB_FILE,
    DEFAULT_LOGS_DIR,
    DEFAULT_MEMORY_FILE,
    DEFAULT_SNAPSHOT_DIR,
    MODULE_DATA_DIR,
)
from modules.self_healing_engine.config.recovery_config import RecoveryConfig
from modules.self_healing_engine.config.repair_rules import RepairRulesConfig


@dataclass(slots=True)
class HealingConfig:
    """Top-level configuration for the Self-Healing Engine."""

    name: str = "self_healing_engine"
    version: int = 1
    enabled: bool = True
    health_check_interval_seconds: int = 30
    max_concurrent_repairs: int = 2
    auto_repair_enabled: bool = True
    approval_required_above_risk: str = "medium"
    repair_rules: RepairRulesConfig = field(default_factory=RepairRulesConfig)
    recovery: RecoveryConfig = field(default_factory=RecoveryConfig)
    automation: AutomationConfig = field(default_factory=AutomationConfig)
    project_root: str = ""
    data_dir: str = ""
    db_file: str = DEFAULT_DB_FILE
    snapshot_dir: str = DEFAULT_SNAPSHOT_DIR
    logs_dir: str = DEFAULT_LOGS_DIR
    memory_file: str = DEFAULT_MEMORY_FILE

    @classmethod
    def from_env(cls) -> "HealingConfig":
        return cls(
            enabled=env_bool("ENABLED", True),
            health_check_interval_seconds=env_int(
                "HEALTH_CHECK_INTERVAL_SECONDS", 30
            ),
            max_concurrent_repairs=env_int("MAX_CONCURRENT_REPAIRS", 2),
            auto_repair_enabled=env_bool("AUTO_REPAIR_ENABLED", True),
            approval_required_above_risk=env_str(
                "APPROVAL_REQUIRED_ABOVE_RISK", "medium"
            ),
            repair_rules=RepairRulesConfig.from_env(),
            recovery=RecoveryConfig.from_env(),
            automation=AutomationConfig.from_env(),
        )

    def resolve(self, project_root: str | Path | None = None) -> None:
        """Resolve runtime data paths relative to the given project root."""
        base = Path(project_root).resolve() if project_root else Path.cwd().resolve()
        self.project_root = str(base)
        data_root = base / DATA_DIR_NAME / MODULE_DATA_DIR
        self.data_dir = str(data_root)
        self.db_file = str(data_root / DEFAULT_DB_FILE)
        self.snapshot_dir = str(data_root / self.recovery.snapshot_dir)
        self.logs_dir = str(data_root / DEFAULT_LOGS_DIR)
        self.memory_file = str(data_root / DEFAULT_MEMORY_FILE)

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
            "health_check_interval_seconds": self.health_check_interval_seconds,
            "max_concurrent_repairs": self.max_concurrent_repairs,
            "auto_repair_enabled": self.auto_repair_enabled,
            "approval_required_above_risk": self.approval_required_above_risk,
            "repair_rules": self.repair_rules.to_dict(),
            "recovery": self.recovery.to_dict(),
            "automation": self.automation.to_dict(),
        }
