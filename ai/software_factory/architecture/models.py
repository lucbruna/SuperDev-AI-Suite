"""Data models for software architecture."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ComponentType(Enum):
    MODULE = "module"
    SERVICE = "service"
    DATABASE = "database"
    QUEUE = "queue"
    CACHE = "cache"
    API = "api"
    UI = "ui"
    LIBRARY = "library"
    GATEWAY = "gateway"
    WORKER = "worker"


class ConnectorType(Enum):
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    EVENT = "event"
    STREAM = "stream"
    RPC = "rpc"
    HTTP = "http"
    GRPC = "grpc"
    MESSAGE_QUEUE = "message_queue"


class PatternType(Enum):
    MICROSERVICES = "microservices"
    MONOLITH = "monolith"
    EVENT_DRIVEN = "event_driven"
    LAYERED = "layered"
    HEXAGONAL = "hexagonal"
    CQRS = "cqrs"
    SAGA = "saga"
    CIRCUIT_BREAKER = "circuit_breaker"
    API_GATEWAY = "api_gateway"


@dataclass
class ArchitectureComponent:
    """A component in the architecture."""

    component_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    component_type: ComponentType = ComponentType.MODULE
    technology: str = ""
    responsibilities: list[str] = field(default_factory=list)
    interfaces: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Connector:
    """Connection between components."""

    connector_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_id: str = ""
    target_id: str = ""
    connector_type: ConnectorType = ConnectorType.SYNCHRONOUS
    protocol: str = ""
    description: str = ""
    bandwidth: str = ""
    latency: str = ""


@dataclass
class ArchitecturePattern:
    """An architectural pattern definition."""

    pattern_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    pattern_type: PatternType = PatternType.LAYERED
    components: list[str] = field(default_factory=list)
    connectors: list[str] = field(default_factory=list)
    trade_offs: dict[str, str] = field(default_factory=dict)


@dataclass
class ArchitectureView:
    """A view of the architecture from a specific perspective."""

    view_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    perspective: str = ""
    components: list[str] = field(default_factory=list)
    connectors: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ArchitectureDecision:
    """An Architecture Decision Record (ADR)."""

    decision_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    status: str = "proposed"
    context: str = ""
    decision: str = ""
    consequences: list[str] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)
    decided_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DesignConstraint:
    """A constraint on the architecture design."""

    constraint_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    constraint_type: str = "technical"
    impact: str = "medium"
    mitigation: str = ""
