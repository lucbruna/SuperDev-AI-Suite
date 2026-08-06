"""Top-level Digital Twin configuration.

Environment prefix: ``SUPERDEV_DT_*``.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.digital_twin.config._env import env_bool, env_int
from modules.digital_twin.config.constants import (
    DATA_DIR_NAME,
    DEFAULT_DB_FILE,
    DEFAULT_LOGS_DIR,
    DEFAULT_MEMORY_FILE,
    DEFAULT_REPORTS_DIR,
    DEFAULT_SNAPSHOT_DIR,
    MODULE_DATA_DIR,
)
from modules.digital_twin.config.memory_config import MemoryConfig
from modules.digital_twin.config.monitoring_config import MonitoringConfig
from modules.digital_twin.config.prediction_config import PredictionConfig
from modules.digital_twin.config.simulation_config import SimulationConfig
from modules.digital_twin.config.sync_config import SyncConfig


@dataclass(slots=True)
class DigitalTwinConfig:
    """Top-level configuration for the Digital Twin runtime."""

    name: str = "digital_twin"
    version: int = 1

    # Twin behaviour.
    enabled: bool = True
    snapshot_retention: int = 50
    autosave_snapshots: bool = True
    max_simultaneous_syncs: int = 2

    # Sub-configs.
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
    prediction: PredictionConfig = field(default_factory=PredictionConfig)
    sync: SyncConfig = field(default_factory=SyncConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)

    # Storage.
    project_root: str = ""
    data_dir: str = ""
    db_file: str = DEFAULT_DB_FILE
    snapshot_dir: str = DEFAULT_SNAPSHOT_DIR
    reports_dir: str = DEFAULT_REPORTS_DIR
    logs_dir: str = DEFAULT_LOGS_DIR
    memory_file: str = DEFAULT_MEMORY_FILE

    @classmethod
    def from_env(cls) -> "DigitalTwinConfig":
        cfg = cls()
        cfg.simulation = SimulationConfig.from_env()
        cfg.prediction = PredictionConfig.from_env()
        cfg.sync = SyncConfig.from_env()
        cfg.monitoring = MonitoringConfig.from_env()
        cfg.memory = MemoryConfig.from_env()
        cfg.enabled = env_bool("ENABLED", cfg.enabled)
        cfg.snapshot_retention = env_int("SNAPSHOT_RETENTION", cfg.snapshot_retention)
        cfg.autosave_snapshots = env_bool("AUTOSAVE_SNAPSHOTS", cfg.autosave_snapshots)
        cfg.max_simultaneous_syncs = env_int(
            "MAX_SIMULTANEOUS_SYNCS", cfg.max_simultaneous_syncs
        )
        return cfg

    def resolve(self, project_root: str | None = None) -> None:
        """Resolve project root and derived data paths."""
        import pathlib

        root = pathlib.Path(project_root).resolve() if project_root else pathlib.Path.cwd().resolve()
        self.project_root = str(root)
        if not self.data_dir:
            self.data_dir = str(root / DATA_DIR_NAME / MODULE_DATA_DIR)
