"""Dependency container for the Digital Twin API."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.digital_twin.config.digital_twin_config import DigitalTwinConfig
from modules.digital_twin.config.permissions import Permissions
from modules.digital_twin.core.digital_twin_manager import DigitalTwinManager


@dataclass(slots=True)
class TwinDependencies:
    """Things every API handler needs, bundled together."""

    manager: DigitalTwinManager | None = None
    config: DigitalTwinConfig | None = None
    permissions: Permissions | None = None
    audit_log: list[dict[str, object]] = field(default_factory=list)
