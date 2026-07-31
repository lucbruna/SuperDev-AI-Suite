from __future__ import annotations

import logging
from typing import Any

from .availability import AvailabilityManager
from .cost_manager import CostManager
from .migration import CloudMigration
from .provider_manager import ProviderManager
from .region_manager import RegionManager
from .resource_manager import ResourceManager


class CloudEngine:
    """Central multi-cloud abstraction engine."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.cloud")
        self.providers = ProviderManager(self)
        self.resources = ResourceManager(self)
        self.costs = CostManager(self)
        self.regions = RegionManager(self)
        self.availability = AvailabilityManager(self)
        self.migration = CloudMigration(self)

    def provision(self, provider: str, resource_type: str, name: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def destroy(self, provider: str, resource_id: str) -> bool:
        raise NotImplementedError

    def estimate_cost(self, provider: str, config: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def get_status(self, provider: str, resource_id: str) -> dict[str, Any]:
        raise NotImplementedError
