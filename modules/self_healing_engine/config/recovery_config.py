"""Recovery configuration: snapshots, checkpoints, backups and rollback."""
from __future__ import annotations

from dataclasses import dataclass

from modules.self_healing_engine.config._env import (
    env_bool,
    env_int,
    env_str,
)
from modules.self_healing_engine.config.constants import DEFAULT_SNAPSHOT_DIR


@dataclass(slots=True)
class RecoveryConfig:
    """Policy governing rollback and restore behaviour."""

    snapshot_dir: str = DEFAULT_SNAPSHOT_DIR
    max_checkpoints: int = 10
    backup_retention_days: int = 30
    backup_enabled: bool = True
    auto_rollback: bool = True
    rollback_on_failure: bool = True
    restore_timeout_seconds: int = 60

    @classmethod
    def from_env(cls) -> "RecoveryConfig":
        return cls(
            snapshot_dir=env_str("SNAPSHOT_DIR", DEFAULT_SNAPSHOT_DIR),
            max_checkpoints=env_int("MAX_CHECKPOINTS", 10),
            backup_retention_days=env_int("BACKUP_RETENTION_DAYS", 30),
            backup_enabled=env_bool("BACKUP_ENABLED", True),
            auto_rollback=env_bool("AUTO_ROLLBACK", True),
            rollback_on_failure=env_bool("ROLLBACK_ON_FAILURE", True),
            restore_timeout_seconds=env_int("RESTORE_TIMEOUT_SECONDS", 60),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "snapshot_dir": self.snapshot_dir,
            "max_checkpoints": self.max_checkpoints,
            "backup_retention_days": self.backup_retention_days,
            "backup_enabled": self.backup_enabled,
            "auto_rollback": self.auto_rollback,
            "rollback_on_failure": self.rollback_on_failure,
            "restore_timeout_seconds": self.restore_timeout_seconds,
        }
