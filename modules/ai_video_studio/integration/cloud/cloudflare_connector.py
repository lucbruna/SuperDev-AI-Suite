"""Cloudflare Connector — CDN/R2 configuration-driven provider."""
from __future__ import annotations

import os
from typing import Any

SERVICES = ("r2", "cdn", "workers", "stream")


class CloudflareConnector:
    """Reports Cloudflare readiness from environment configuration."""

    name = "cloudflare"

    def capabilities(self) -> dict[str, Any]:
        return {
            "provider": self.name,
            "configured": bool(os.environ.get("CLOUDFLARE_API_TOKEN")),
            "services": list(SERVICES),
        }

    def upload_media(self, *, bucket: str = "", key: str = "") -> dict[str, Any]:
        if not bucket or not key:
            return {"ok": False, "error": "bucket and key are required"}
        return {"ok": True, "provider": self.name, "bucket": bucket, "key": key, "dry_run": True}


_cloudflare_connector: CloudflareConnector | None = None


def get_cloudflare_connector() -> CloudflareConnector:
    global _cloudflare_connector
    if _cloudflare_connector is None:
        _cloudflare_connector = CloudflareConnector()
    return _cloudflare_connector
