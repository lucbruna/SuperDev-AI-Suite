from __future__ import annotations

import logging
from typing import Any

from .availability import AvailabilityManager
from .cost_manager import CostManager
from .migration import CloudMigration
from .provider_manager import ProviderManager
from .region_manager import RegionManager
from .resource_manager import ResourceManager

# Base hourly cost per resource type (used by the simulated estimate).
_RESOURCE_HOURLY = {
    "compute": 0.10,
    "storage": 0.05,
    "network": 0.02,
    "database": 0.25,
    "cache": 0.12,
    "dns": 0.01,
    "certificate": 0.01,
}


class CloudEngine:
    """Central multi-cloud abstraction engine (in-memory)."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.cloud")
        self.providers = ProviderManager(self)
        self.resources = ResourceManager(self)
        self.costs = CostManager(self)
        self.regions = RegionManager(self)
        self.availability = AvailabilityManager(self)
        self.migration = CloudMigration(self)
        self._region = "us-east-1"

    def provision(self, provider: str, resource_type: str, name: str, **kwargs: Any) -> dict[str, Any]:
        """Provision a resource through the resource manager."""
        if self.providers.get(provider) is None:
            raise ValueError(f"unknown cloud provider: {provider}")
        return self.resources.create(provider, resource_type, name, **kwargs)

    def destroy(self, provider: str, resource_id: str) -> bool:
        """Destroy a resource (terminated) through the resource manager."""
        return self.resources.delete(provider, resource_id)

    def estimate_cost(self, provider: str, config: dict[str, Any]) -> dict[str, Any]:
        """Estimate monthly cost for a resource configuration."""
        resource_type = config.get("resource_type", "compute")
        hourly = _RESOURCE_HOURLY.get(resource_type, 0.10)
        instances = max(1, int(config.get("instances", 1)))
        monthly = hourly * instances * 24 * 30
        return {
            "provider": provider,
            "resource_type": resource_type,
            "instances": instances,
            "hourly_rate": hourly,
            "monthly_estimate": round(monthly, 2),
        }

    def get_status(self, provider: str, resource_id: str) -> dict[str, Any]:
        return self.resources.get(provider, resource_id)

    def list_resources(self, provider: str | None = None) -> list[dict[str, Any]]:
        return self.resources.list(provider)
