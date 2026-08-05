"""Azure Connector — configuration-driven capability provider (no live calls)."""
from __future__ import annotations

import os
from typing import Any

SERVICES = ("blob", "vm", "media", "speech", "vision")


class AzureConnector:
    """Reports Azure readiness from environment configuration."""

    name = "azure"

    def __init__(self) -> None:
        self.region = os.environ.get("AZURE_REGION", "eastus")

    def capabilities(self) -> dict[str, Any]:
        return {
            "provider": self.name,
            "region": self.region,
            "configured": bool(os.environ.get("AZURE_TENANT_ID")),
            "services": list(SERVICES),
        }

    def upload_media(self, *, container: str = "", blob: str = "") -> dict[str, Any]:
        if not container or not blob:
            return {"ok": False, "error": "container and blob are required"}
        return {"ok": True, "provider": self.name, "container": container, "blob": blob, "dry_run": True}


_azure_connector: AzureConnector | None = None


def get_azure_connector() -> AzureConnector:
    global _azure_connector
    if _azure_connector is None:
        _azure_connector = AzureConnector()
    return _azure_connector
