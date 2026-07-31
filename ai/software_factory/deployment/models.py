"""Data models for deployment management."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DeploymentStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


class EnvironmentType(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"
    QA = "qa"


@dataclass
class Deployment:
    """A deployment record."""
    deployment_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    version: str = ""
    environment: str = ""
    status: DeploymentStatus = DeploymentStatus.PENDING
    steps: list[str] = field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Environment:
    """A deployment environment."""
    env_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    environment_type: EnvironmentType = EnvironmentType.DEVELOPMENT
    url: str = ""
    config: dict[str, Any] = field(default_factory=dict)
    active: bool = True


@dataclass
class Release:
    """A release record."""
    release_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    version: str = ""
    name: str = ""
    description: str = ""
    changelog: list[str] = field(default_factory=list)
    deployed_environments: list[str] = field(default_factory=list)
    released_at: datetime | None = None


@dataclass
class RollbackPlan:
    """A rollback plan for a deployment."""
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    deployment_id: str = ""
    steps: list[str] = field(default_factory=list)
    triggers: list[str] = field(default_factory=list)
    estimated_time: float = 0.0


@dataclass
class DeploymentConfig:
    """Configuration for a deployment."""
    config_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    auto_rollback: bool = True
    health_check_url: str = ""
    health_check_timeout: float = 60.0
    max_retries: int = 3
    notification_channels: list[str] = field(default_factory=list)
