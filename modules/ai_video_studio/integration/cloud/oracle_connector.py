"""Oracle Connector — OCI configuration-driven provider."""
from __future__ import annotations

import os
from typing import Any

SERVICES = ("object_storage", "compute", "ai_language", "speech")


class OracleConnector:
    """Reports Oracle Cloud readiness from environment configuration."""

    name = "oracle"

    def capabilities(self) -> dict[str, Any]:
        return {
            "provider": self.name,
            "configured": bool(os.environ.get("OCI_CONFIG_FILE") or os.environ.get("OCI_CLI_AUTH")),
            "services": list(SERVICES),
        }

    def upload_media(self, *, namespace: str = "", bucket: str = "", object: str = "") -> dict[str, Any]:
        if not bucket or not object:
            return {"ok": False, "error": "bucket and object are required"}
        return {"ok": True, "provider": self.name, "namespace": namespace,
                "bucket": bucket, "object": object, "dry_run": True}


_oracle_connector: OracleConnector | None = None


def get_oracle_connector() -> OracleConnector:
    global _oracle_connector
    if _oracle_connector is None:
        _oracle_connector = OracleConnector()
    return _oracle_connector
