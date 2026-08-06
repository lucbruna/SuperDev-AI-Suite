"""Permission model for the AI Evolution Engine.

The engine never modifies the project: permissions gate *what* it may observe
and *which* recommendations may be emitted or escalated.
"""
from __future__ import annotations

from dataclasses import dataclass

from modules.ai_evolution_engine.config._env import env_bool


@dataclass(slots=True)
class Permissions:
    """Read-only observation permissions (no mutation is ever allowed)."""

    can_scan_filesystem: bool = True
    can_read_git_history: bool = True
    can_read_architecture_graph: bool = True
    can_read_digital_twin: bool = True
    can_emit_architecture: bool = True
    can_emit_dependency: bool = True
    can_emit_performance: bool = True
    can_emit_security: bool = True
    can_emit_modernization: bool = True

    @classmethod
    def from_env(cls) -> "Permissions":
        return cls(
            can_scan_filesystem=env_bool(
                "AI_EVOLUTION_SCAN_FS", True
            ),
            can_read_git_history=env_bool(
                "AI_EVOLUTION_READ_GIT", True
            ),
            can_read_architecture_graph=env_bool(
                "AI_EVOLUTION_READ_GRAPH", True
            ),
            can_read_digital_twin=env_bool(
                "AI_EVOLUTION_READ_TWIN", True
            ),
        )
