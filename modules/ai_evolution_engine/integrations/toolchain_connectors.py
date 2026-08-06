"""Toolchain connectors: git, GitHub, Docker, Kubernetes, MCP.

These connectors never execute network or mutating commands. Availability is
detected from the filesystem/environment only, keeping the engine
deterministic.
"""
from __future__ import annotations

import shutil
from typing import Any

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.integrations.integration_registry import (
    IntegrationConnector,
)


class GitConnector(IntegrationConnector):
    name = "git"
    description = "Local git toolchain availability."

    def check_available(self) -> bool:
        return shutil.which("git") is not None

    def collect(self, ctx: EvolutionContext) -> dict[str, Any]:
        root = ctx.get_artifact("superdev_root", "") or ""
        is_repo = False
        if root:
            import os

            is_repo = os.path.isdir(os.path.join(root, ".git"))
        return {
            "available": self.check_available(),
            "name": self.name,
            "is_git_repo": is_repo,
        }


class GitHubConnector(IntegrationConnector):
    name = "github"
    description = "GitHub CLI/token availability."

    def check_available(self) -> bool:
        return shutil.which("gh") is not None

    def collect(self, ctx: EvolutionContext) -> dict[str, Any]:
        return {"available": self.check_available(), "name": self.name}


class DockerConnector(IntegrationConnector):
    name = "docker"
    description = "Docker CLI availability."

    def check_available(self) -> bool:
        return shutil.which("docker") is not None

    def collect(self, ctx: EvolutionContext) -> dict[str, Any]:
        return {"available": self.check_available(), "name": self.name}


class KubernetesConnector(IntegrationConnector):
    name = "kubernetes"
    description = "kubectl CLI availability."

    def check_available(self) -> bool:
        return shutil.which("kubectl") is not None

    def collect(self, ctx: EvolutionContext) -> dict[str, Any]:
        return {"available": self.check_available(), "name": self.name}


class MCPConnector(IntegrationConnector):
    name = "mcp"
    description = "MCP server availability via configuration artifact."

    def check_available(self) -> bool:
        return bool(self._configured())

    def _configured(self) -> list[str]:
        from modules.ai_evolution_engine.config._env import env_str

        raw = env_str("MCP_SERVERS", "")
        return [item.strip() for item in raw.split(",") if item.strip()]

    def collect(self, ctx: EvolutionContext) -> dict[str, Any]:
        servers = self._configured()
        return {
            "available": bool(servers),
            "name": self.name,
            "servers": servers,
        }
