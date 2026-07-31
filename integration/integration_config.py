from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class IntegrationConfig:
    """Configuration for the Integration & API Engine."""

    workspace_id: str = "default"
    gateway_host: str = "0.0.0.0"
    gateway_port: int = 8080
    default_rate_limit: int = 100
    default_timeout: float = 30.0
    max_payload_size: int = 1048576
    enable_auth: bool = True
    enable_webhooks: bool = True
    enable_messaging: bool = True
    webhook_max_retries: int = 3
    sync_interval: int = 300
    monitoring_interval: int = 30
    marketplace_url: str = "https://marketplace.superdev.ai"
    storage_path: str = ".integration"
    extra: dict[str, Any] = field(default_factory=dict)

    def merge(self, overrides: dict[str, Any]) -> IntegrationConfig:
        for key, value in overrides.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self.extra[key] = value
        return self
