"""DevOps data models."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field
import time, uuid

class ServerState(Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    PROVISIONING = "provisioning"
    TERMINATED = "terminated"
    ERROR = "error"

class ContainerState(Enum):
    CREATED = "created"
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"

class PipelineState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

@dataclass
class Server:
    server_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    provider: str = "aws"
    region: str = "us-east-1"
    cpu: int = 4
    memory_gb: int = 16
    disk_gb: int = 100
    state: ServerState = ServerState.PROVISIONING
    ip_address: str = ""
    created_at: float = field(default_factory=time.time)

@dataclass
class Container:
    container_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    image: str = ""
    state: ContainerState = ContainerState.CREATED
    ports: List[int] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

@dataclass
class Pipeline:
    pipeline_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    stages: List[str] = field(default_factory=list)
    state: PipelineState = PipelineState.IDLE
    current_stage: int = 0
    created_at: float = field(default_factory=time.time)

@dataclass
class Deployment:
    deployment_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    version: str = ""
    strategy: str = "rolling"
    status: str = "pending"
    replicas: int = 1
    created_at: float = field(default_factory=time.time)

@dataclass
class BackupJob:
    job_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    source: str = ""
    destination: str = ""
    schedule: str = "daily"
    last_run: float = 0.0
    status: str = "idle"
