from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DevOpsEnvironment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class DevOpsResource(Enum):
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"
    DNS = "dns"
    CERTIFICATE = "certificate"


@dataclass
class DevOpsService:
    """Represents a deployable service."""
    name: str
    service_type: str
    version: str = "latest"
    environment: str = "development"
    config: dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    endpoints: list[str] = field(default_factory=list)
