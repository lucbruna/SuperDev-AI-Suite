"""Cloud Connector — facade over the cloud provider connectors."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration.cloud.aws_connector import get_aws_connector
from modules.ai_video_studio.integration.cloud.azure_connector import get_azure_connector
from modules.ai_video_studio.integration.cloud.cloudflare_connector import (
    get_cloudflare_connector,
)
from modules.ai_video_studio.integration.cloud.google_connector import get_google_connector
from modules.ai_video_studio.integration.cloud.oracle_connector import get_oracle_connector
from modules.ai_video_studio.integration.connector_base import DomainConnector


class CloudConnector(DomainConnector):
    """AWS, Azure, Google, Cloudflare and Oracle capability reports."""

    domain = "cloud"
    description = "AWS, Azure, Google, Cloudflare and Oracle connectors"

    def __init__(self) -> None:
        super().__init__()
        self._register("capabilities", self._capabilities)
        self._register("upload_media", self._upload)

    def _capabilities(self, data: dict[str, Any]) -> dict[str, Any]:
        return {
            "providers": [
                get_aws_connector().capabilities(),
                get_azure_connector().capabilities(),
                get_google_connector().capabilities(),
                get_cloudflare_connector().capabilities(),
                get_oracle_connector().capabilities(),
            ]
        }

    def _upload(self, data: dict[str, Any]) -> dict[str, Any]:
        provider = data.get("provider", "aws")
        handlers = {
            "aws": get_aws_connector(), "azure": get_azure_connector(),
            "google": get_google_connector(), "cloudflare": get_cloudflare_connector(),
            "oracle": get_oracle_connector(),
        }
        connector = handlers.get(provider)
        if connector is None:
            return {"ok": False, "error": f"unknown provider '{provider}'"}
        return connector.upload_media(**data.get("args", {}))


_cloud_connector: CloudConnector | None = None


def get_cloud_connector() -> CloudConnector:
    global _cloud_connector
    if _cloud_connector is None:
        _cloud_connector = CloudConnector()
    return _cloud_connector
