"""AWS Connector — configuration-driven capability provider (no live calls)."""
from __future__ import annotations

import os
from typing import Any

SERVICES = ("s3", "ec2", "lambda", "transcribe", "rekognition")


class AWSConnector:
    """Reports AWS readiness from environment configuration."""

    name = "aws"

    def __init__(self) -> None:
        self.region = os.environ.get("AWS_REGION", "us-east-1")

    def capabilities(self) -> dict[str, Any]:
        return {
            "provider": self.name,
            "region": self.region,
            "configured": bool(os.environ.get("AWS_ACCESS_KEY_ID")),
            "services": list(SERVICES),
        }

    def upload_media(self, *, bucket: str = "", key: str = "") -> dict[str, Any]:
        if not bucket or not key:
            return {"ok": False, "error": "bucket and key are required"}
        return {"ok": True, "provider": self.name, "bucket": bucket, "key": key, "dry_run": True}


_aws_connector: AWSConnector | None = None


def get_aws_connector() -> AWSConnector:
    global _aws_connector
    if _aws_connector is None:
        _aws_connector = AWSConnector()
    return _aws_connector
