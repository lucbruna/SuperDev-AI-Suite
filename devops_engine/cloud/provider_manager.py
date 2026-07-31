"""Cloud provider profiles and selection (Volume 37, Fase 2)."""

from __future__ import annotations

from typing import Any

from devops_engine.devops_models import CloudProvider

_PROFILES: dict[CloudProvider, dict[str, Any]] = {
    CloudProvider.AWS: {
        "cost_factor": 1.0,
        "regions": ["us-east-1", "us-west-2", "eu-west-1"],
    },
    CloudProvider.GCP: {
        "cost_factor": 1.05,
        "regions": ["us-central1", "europe-west1"],
    },
    CloudProvider.AZURE: {
        "cost_factor": 1.1,
        "regions": ["eastus", "westeurope"],
    },
    CloudProvider.ORACLE: {
        "cost_factor": 0.9,
        "regions": ["us-ashburn-1"],
    },
    CloudProvider.PRIVATE: {
        "cost_factor": 0.7,
        "regions": ["private-1"],
    },
    CloudProvider.ON_PREMISE: {
        "cost_factor": 0.6,
        "regions": ["dc-1"],
    },
}


class ProviderManager:
    """Selects providers and exposes per-provider cost/region profiles."""

    def select(self, name: str | None) -> CloudProvider:
        normalized = (name or "").strip().lower()
        for provider in CloudProvider:
            if (provider.value == normalized
                    or provider.name.lower() == normalized):
                return provider
        return CloudProvider.PRIVATE

    def profile(self, provider: CloudProvider) -> dict[str, Any]:
        return dict(_PROFILES.get(provider, {"cost_factor": 1.0,
                                             "regions": ["us-east-1"]}))

    def cost_factor(self, provider: CloudProvider) -> float:
        return float(self.profile(provider).get("cost_factor", 1.0))

    def default_region(self, provider: CloudProvider) -> str:
        regions = self.profile(provider).get("regions", ["us-east-1"])
        return str(regions[0]) if regions else "us-east-1"

    def list_providers(self) -> list[CloudProvider]:
        return list(CloudProvider)
