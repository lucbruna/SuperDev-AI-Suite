"""Configuration for the DevOps & Cloud Infrastructure Engine (V37)."""

from __future__ import annotations

from typing import Any

from devops_engine.devops_models import CloudProvider


class DevopsConfig:
    """Runtime configuration for the engine."""

    def __init__(self, overrides: dict[str, Any] | None = None) -> None:
        self.provider: CloudProvider = CloudProvider.AWS
        self.region: str = "us-east-1"
        self.default_cpu: int = 2
        self.default_memory_gb: int = 4
        self.default_replicas: int = 2
        self.approval_threshold: float = 50000.0
        self.max_open_alerts: int = 100
        self.retention_days: int = 30
        self.currency: str = "BRL"
        self.env: str = "production"
        self.backup_encrypted: bool = True
        self.apply(overrides or {})

    def apply(self, overrides: dict[str, Any]) -> None:
        for key, value in (overrides or {}).items():
            if key == "provider" and isinstance(value, str):
                value = CloudProvider(value)
            if hasattr(self, key):
                setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def merge(self, other: dict[str, Any]) -> "DevopsConfig":
        merged = DevopsConfig(self.snapshot())
        merged.apply(other)
        return merged

    def snapshot(self) -> dict[str, Any]:
        return {
            "provider": self.provider.value,
            "region": self.region,
            "default_cpu": self.default_cpu,
            "default_memory_gb": self.default_memory_gb,
            "default_replicas": self.default_replicas,
            "approval_threshold": self.approval_threshold,
            "max_open_alerts": self.max_open_alerts,
            "retention_days": self.retention_days,
            "currency": self.currency,
            "env": self.env,
            "backup_encrypted": self.backup_encrypted,
        }
