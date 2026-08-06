"""Security policy: what the Self-Healing Engine may and may not touch."""
from __future__ import annotations

from dataclasses import dataclass

from modules.self_healing_engine.config._env import (
    env_bool,
    env_str,
)


@dataclass(slots=True)
class SecurityPolicy:
    """Guardrails limiting the blast radius of automated repairs."""

    allow_path_modifications: bool = True
    allow_config_modifications: bool = True
    allow_dependency_modifications: bool = True
    allow_code_modifications: bool = False
    allow_network_operations: bool = False
    allow_destructive_operations: bool = False
    protected_paths: tuple[str, ...] = (".git", ".superdev")
    forbidden_patterns: tuple[str, ...] = ("rm -rf", "drop database")

    @classmethod
    def from_env(cls) -> "SecurityPolicy":
        return cls(
            allow_path_modifications=env_bool("ALLOW_PATH_MODIFICATIONS", True),
            allow_config_modifications=env_bool(
                "ALLOW_CONFIG_MODIFICATIONS", True
            ),
            allow_dependency_modifications=env_bool(
                "ALLOW_DEPENDENCY_MODIFICATIONS", True
            ),
            allow_code_modifications=env_bool("ALLOW_CODE_MODIFICATIONS", False),
            allow_network_operations=env_bool("ALLOW_NETWORK_OPERATIONS", False),
            allow_destructive_operations=env_bool(
                "ALLOW_DESTRUCTIVE_OPERATIONS", False
            ),
            protected_paths=tuple(
                part.strip()
                for part in env_str("PROTECTED_PATHS", ".git,.superdev").split(",")
                if part.strip()
            ),
            forbidden_patterns=tuple(
                part.strip()
                for part in env_str("FORBIDDEN_PATTERNS", "rm -rf,drop database")
                .split(",")
                if part.strip()
            ),
        )

    def is_path_protected(self, path: str) -> bool:
        normalized = path.replace("\\", "/")
        return any(f"/{p}/" in f"/{normalized}/" for p in self.protected_paths)

    def contains_forbidden_pattern(self, command: str) -> bool:
        lowered = command.lower()
        return any(pattern.lower() in lowered for pattern in self.forbidden_patterns)

    def to_dict(self) -> dict[str, object]:
        return {
            "allow_path_modifications": self.allow_path_modifications,
            "allow_config_modifications": self.allow_config_modifications,
            "allow_dependency_modifications": self.allow_dependency_modifications,
            "allow_code_modifications": self.allow_code_modifications,
            "allow_network_operations": self.allow_network_operations,
            "allow_destructive_operations": self.allow_destructive_operations,
            "protected_paths": list(self.protected_paths),
            "forbidden_patterns": list(self.forbidden_patterns),
        }
