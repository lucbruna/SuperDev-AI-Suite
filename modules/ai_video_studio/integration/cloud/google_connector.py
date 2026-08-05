"""Google Connector — configuration-driven capability provider (no live calls)."""
from __future__ import annotations

import os
from typing import Any

SERVICES = ("gcs", "gce", "video", "speech", "vertex")


class GoogleConnector:
    """Reports Google Cloud readiness from environment configuration."""

    name = "google"

    def __init__(self) -> None:
        self.region = os.environ.get("GOOGLE_REGION", "us-central1")

    def capabilities(self) -> dict[str, Any]:
        return {
            "provider": self.name,
            "region": self.region,
            "configured": bool(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")),
            "services": list(SERVICES),
        }

    def upload_media(self, *, bucket: str = "", object: str = "") -> dict[str, Any]:
        if not bucket or not object:
            return {"ok": False, "error": "bucket and object are required"}
        return {"ok": True, "provider": self.name, "bucket": bucket, "object": object, "dry_run": True}


_google_connector: GoogleConnector | None = None


def get_google_connector() -> GoogleConnector:
    global _google_connector
    if _google_connector is None:
        _google_connector = GoogleConnector()
    return _google_connector
