"""Cloud Provider — provider registry and capabilities (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_PROVIDERS = {
    "aws": {"regions": ["us-east-1", "eu-west-1", "sa-east-1"], "storage_class": "S3"},
    "gcp": {"regions": ["us-central1", "europe-west1", "southamerica-east1"], "storage_class": "GCS"},
    "azure": {"regions": ["eastus", "westeurope", "brazilsouth"], "storage_class": "Blob"},
}


class CloudProvider:
    """Describe available cloud providers and their capabilities."""

    def list_providers(self) -> dict:
        return {name: info["storage_class"] for name, info in _PROVIDERS.items()}

    def regions(self, *, provider: str = "") -> list[str]:
        info = _PROVIDERS.get(provider.lower(), {})
        return info.get("regions", [])

    def recommend(self, *, provider: str = "", region: str = "") -> dict:
        """Recommend a storage class for the given provider/region."""
        info = _PROVIDERS.get(provider.lower(), _PROVIDERS["aws"])
        regions = info["regions"]
        chosen = region if region in regions else (regions[0] if regions else "us-east-1")
        return {"provider": provider or "aws", "storage_class": info["storage_class"], "region": chosen}

    def stats(self) -> dict[str, int]:
        return {"providers": len(_PROVIDERS)}


_PROVIDER: CloudProvider | None = None


def get_cloud_provider() -> CloudProvider:
    """Get the module-level singleton cloud provider registry."""
    global _PROVIDER
    if _PROVIDER is None:
        _PROVIDER = CloudProvider()
    return _PROVIDER
