"""Models for the DevOps & Cloud Infrastructure Engine (Volume 37)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CloudProvider(Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ORACLE = "oracle"
    PRIVATE = "private"
    ON_PREMISE = "on_premise"


class ResourceType(Enum):
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORK = "network"
    CACHE = "cache"
    LOAD_BALANCER = "load_balancer"


class ResourceStatus(Enum):
    PROVISIONING = "provisioning"
    RUNNING = "running"
    STOPPED = "stopped"
    DEGRADED = "degraded"
    FAILED = "failed"
    TERMINATED = "terminated"


class ContainerStatus(Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    UNHEALTHY = "unhealthy"
    FAILED = "failed"


class ImageStatus(Enum):
    PENDING = "pending"
    BUILT = "built"
    PUSHED = "pushed"
    FAILED = "failed"


class ClusterStatus(Enum):
    PROVISIONING = "provisioning"
    READY = "ready"
    DEGRADED = "degraded"
    DOWN = "down"


class PodStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CRASHED = "crashed"


class DeploymentStatus(Enum):
    PENDING = "pending"
    ROLLING = "rolling"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class ServiceStatus(Enum):
    ACTIVE = "active"
    DRAINING = "draining"
    STOPPED = "stopped"


class PipelineStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BuildStatus(Enum):
    PENDING = "pending"
    BUILDING = "building"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ReleaseStatus(Enum):
    DRAFT = "draft"
    DEPLOYED = "deployed"
    ROLLED_BACK = "rolled_back"


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class BackupType(Enum):
    FULL = "full"
    INCREMENTAL = "incremental"


class BackupStatus(Enum):
    SCHEDULED = "scheduled"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class RestoreStatus(Enum):
    PENDING = "pending"
    RESTORING = "restoring"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class RecoveryStatus(Enum):
    DETECTED = "detected"
    FAILOVER = "failover"
    RESTORING = "restoring"
    RECOVERED = "recovered"
    FAILED = "failed"


class IncidentStatus(Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"


class Severity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def rank(self) -> int:
        return {"low": 0, "medium": 1, "high": 2, "critical": 3}[self.value]


@dataclass
class Server:
    """A provisioned compute instance."""
    server_id: str
    name: str
    provider: CloudProvider = CloudProvider.AWS
    instance_type: str = "t3.medium"
    cpu: int = 2
    memory_gb: int = 4
    region: str = "us-east-1"
    status: ResourceStatus = ResourceStatus.PROVISIONING
    ip_address: str = ""
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Resource:
    """A generic cloud resource with a cost per hour."""
    resource_id: str
    name: str
    kind: ResourceType = ResourceType.COMPUTE
    provider: CloudProvider = CloudProvider.AWS
    region: str = "us-east-1"
    status: ResourceStatus = ResourceStatus.PROVISIONING
    cost_per_hour: float = 0.0
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Container:
    """A running container instance."""
    container_id: str
    name: str
    image: str = ""
    status: ContainerStatus = ContainerStatus.CREATED
    ports: list[int] = field(default_factory=list)
    cpu: int = 1
    memory_mb: int = 512
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Image:
    """A built container image."""
    image_id: str
    name: str
    tag: str = "latest"
    digest: str = ""
    status: ImageStatus = ImageStatus.PENDING
    size_bytes: int = 0
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Cluster:
    """A Kubernetes cluster."""
    cluster_id: str
    name: str
    provider: CloudProvider = CloudProvider.AWS
    region: str = "us-east-1"
    nodes: int = 3
    status: ClusterStatus = ClusterStatus.PROVISIONING
    version: str = "1.30"
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Pod:
    """A Kubernetes pod."""
    pod_id: str
    name: str
    cluster_id: str = ""
    image: str = ""
    replicas: int = 1
    status: PodStatus = PodStatus.PENDING
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Deployment:
    """A Kubernetes deployment workload."""
    deployment_id: str
    name: str
    cluster_id: str = ""
    image: str = ""
    replicas: int = 1
    desired: int = 1
    status: DeploymentStatus = DeploymentStatus.PENDING
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Service:
    """A Kubernetes service exposing a workload."""
    service_id: str
    name: str
    cluster_id: str = ""
    selector: str = ""
    ports: list[int] = field(default_factory=list)
    status: ServiceStatus = ServiceStatus.ACTIVE
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Pipeline:
    """A CI/CD pipeline definition and run state."""
    pipeline_id: str
    name: str
    status: PipelineStatus = PipelineStatus.PENDING
    steps: list[str] = field(default_factory=list)
    started_at: float = 0.0
    finished_at: float = 0.0
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Build:
    """A single build executed by a pipeline."""
    build_id: str
    pipeline_id: str = ""
    commit: str = ""
    status: BuildStatus = BuildStatus.PENDING
    duration: float = 0.0
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Release:
    """A released version of an application."""
    release_id: str
    pipeline_id: str = ""
    version: str = "1.0.0"
    status: ReleaseStatus = ReleaseStatus.DRAFT
    deployed_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthCheckResult:
    """Result of a health probe against a target."""
    check_id: str
    target: str
    status: HealthStatus = HealthStatus.UNKNOWN
    latency_ms: float = 0.0
    checked_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricSample:
    """A single metric observation."""
    metric_id: str
    name: str
    value: float = 0.0
    unit: str = ""
    source: str = ""
    sampled_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class LogEntry:
    """A collected log line."""
    log_id: str
    source: str
    level: str = "info"
    message: str = ""
    host: str = ""
    timestamp: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BackupJob:
    """A scheduled or executed backup."""
    backup_id: str
    target: str
    backup_type: BackupType = BackupType.FULL
    status: BackupStatus = BackupStatus.SCHEDULED
    size_bytes: int = 0
    encrypted: bool = True
    started_at: float = 0.0
    finished_at: float = 0.0
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Snapshot:
    """A point-in-time snapshot produced by a backup."""
    snapshot_id: str
    backup_id: str = ""
    name: str = ""
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RestoreJob:
    """A restore operation from a backup."""
    restore_id: str
    backup_id: str
    target: str = ""
    status: RestoreStatus = RestoreStatus.PENDING
    started_at: float = 0.0
    finished_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Incident:
    """A detected production incident."""
    incident_id: str
    title: str
    severity: Severity = Severity.WARNING
    status: IncidentStatus = IncidentStatus.OPEN
    source: str = ""
    detected_at: float = 0.0
    resolved_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AutoscalePolicy:
    """A scaling policy bound to a cluster or service."""
    policy_id: str
    cluster_id: str
    min_replicas: int = 1
    max_replicas: int = 10
    cpu_threshold: float = 0.75
    metric: str = "cpu"
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CostRecord:
    """A cost line item for a resource."""
    cost_id: str
    provider: CloudProvider = CloudProvider.AWS
    region: str = "us-east-1"
    resource: str = ""
    amount: float = 0.0
    period: str = ""
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CostRecommendation:
    """A suggested cost optimization."""
    recommendation_id: str
    resource: str
    action: str = ""
    estimated_saving: float = 0.0
    priority: str = "medium"
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
