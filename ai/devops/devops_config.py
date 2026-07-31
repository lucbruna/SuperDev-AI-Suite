"""DevOps configuration."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class CloudProvider(Enum):
    AWS = "aws"
    AZURE = "azure"
    GOOGLE_CLOUD = "gcp"
    PRIVATE = "private"
    HYBRID = "hybrid"

class DeployStrategy(Enum):
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    ROLLING = "rolling"
    RECREATE = "recreate"

@dataclass
class InfrastructureLimits:
    max_servers: int = 1000
    max_containers: int = 10000
    max_clusters: int = 50
    max_nodes: int = 500
    max_pods: int = 10000

@dataclass
class DevOpsConfig:
    cloud_provider: CloudProvider = CloudProvider.AWS
    deploy_strategy: DeployStrategy = DeployStrategy.ROLLING
    limits: InfrastructureLimits = field(default_factory=InfrastructureLimits)
    auto_scaling: bool = True
    auto_backup: bool = True
    disaster_recovery: bool = True
    monitoring_enabled: bool = True
    secrets_rotation: bool = True
    security_scanning: bool = True
    debug_mode: bool = False
