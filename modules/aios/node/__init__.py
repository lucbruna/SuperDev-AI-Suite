"""Node package — Node.js runtime toolchain (Vol 12, Fase 18)."""
from __future__ import annotations

from modules.aios.node.bun import BunManager, BunUnavailableError
from modules.aios.node.jest import JestRunner, JestUnavailableError
from modules.aios.node.node_client import (
    NodeClient,
    NodeUnavailableError,
    require_node_action,
)
from modules.aios.node.node_runtime import NodeRuntime, get_node_runtime
from modules.aios.node.npm import NpmManager, NpmUnavailableError
from modules.aios.node.package_manager import (
    PackageManager,
    PackageManagerUnavailableError,
)
from modules.aios.node.pnpm import PnpmManager, PnpmUnavailableError
from modules.aios.node.vitest import VitestRunner, VitestUnavailableError
from modules.aios.node.yarn import YarnManager, YarnUnavailableError

__all__ = [
    "BunManager",
    "BunUnavailableError",
    "JestRunner",
    "JestUnavailableError",
    "NodeClient",
    "NodeRuntime",
    "NodeUnavailableError",
    "get_node_runtime",
    "NpmManager",
    "NpmUnavailableError",
    "PackageManager",
    "PackageManagerUnavailableError",
    "PnpmManager",
    "PnpmUnavailableError",
    "require_node_action",
    "VitestRunner",
    "VitestUnavailableError",
    "YarnManager",
    "YarnUnavailableError",
]
