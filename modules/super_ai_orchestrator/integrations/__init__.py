"""Graceful connectors to sibling modules and the toolchain."""
from __future__ import annotations

from modules.super_ai_orchestrator.integrations.base import Connector, ConnectorInfo
from modules.super_ai_orchestrator.integrations.registry import ConnectorRegistry
from modules.super_ai_orchestrator.integrations.sibling import make_sibling_connectors
from modules.super_ai_orchestrator.integrations.toolchain import make_toolchain_connectors

__all__ = [
    "Connector",
    "ConnectorInfo",
    "ConnectorRegistry",
    "make_sibling_connectors",
    "make_toolchain_connectors",
]
