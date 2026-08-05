"""Integrations registry for external tool adapters."""
from __future__ import annotations

from modules.architecture_intelligence.integrations.registry import (
    IntegrationRegistry,
    get_integration_registry,
)

__all__ = ["IntegrationRegistry", "get_integration_registry"]
