"""Memory configuration for the Digital Twin module.

Environment prefix: ``SUPERDEV_DT_MEM_*``.
"""
from __future__ import annotations

from dataclasses import dataclass

from modules.digital_twin.config._env import env_bool, env_int, env_str


@dataclass(slots=True)
class MemoryConfig:
    """Configuration for the twin's persistent memory."""

    max_entries: int = 1000
    persistence_enabled: bool = True
    memory_file: str = "twin_memory.json"

    @classmethod
    def from_env(cls) -> "MemoryConfig":
        cfg = cls()
        cfg.max_entries = env_int("MEM_MAX_ENTRIES", cfg.max_entries)
        cfg.persistence_enabled = env_bool("MEM_PERSISTENCE", cfg.persistence_enabled)
        cfg.memory_file = env_str("MEM_FILE", cfg.memory_file)
        return cfg
