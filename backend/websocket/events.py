from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any


class EventType(Enum):
    CONNECTION_ESTABLISHED = auto()
    CONNECTION_CLOSED = auto()
    MESSAGE_RECEIVED = auto()
    MESSAGE_SENT = auto()
    ERROR = auto()
    AGENT_STARTED = auto()
    AGENT_COMPLETED = auto()
    AGENT_FAILED = auto()
    WORKFLOW_STARTED = auto()
    WORKFLOW_COMPLETED = auto()
    WORKFLOW_FAILED = auto()
    LOG_MESSAGE = auto()
    METRIC_UPDATE = auto()


@dataclass
class WSEvent:
    type: EventType
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.name,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
        }


@dataclass
class EventBuilder:
    type: EventType
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.name,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
        }

    @classmethod
    def connection_event(cls, connection_id: str, status: str) -> "EventBuilder":
        return cls(
            type=EventType.CONNECTION_ESTABLISHED,
            payload={"connection_id": connection_id, "status": status},
        )

    @classmethod
    def agent_event(cls, agent_id: str, status: str, **kwargs) -> "EventBuilder":
        event_map = {
            "started": EventType.AGENT_STARTED,
            "completed": EventType.AGENT_COMPLETED,
            "failed": EventType.AGENT_FAILED,
        }
        return cls(
            type=event_map.get(status, EventType.LOG_MESSAGE),
            payload={"agent_id": agent_id, "status": status, **kwargs},
        )

    @classmethod
    def workflow_event(cls, workflow_id: str, status: str, **kwargs) -> "EventBuilder":
        event_map = {
            "started": EventType.WORKFLOW_STARTED,
            "completed": EventType.WORKFLOW_COMPLETED,
            "failed": EventType.WORKFLOW_FAILED,
        }
        return cls(
            type=event_map.get(status, EventType.LOG_MESSAGE),
            payload={"workflow_id": workflow_id, "status": status, **kwargs},
        )

    @classmethod
    def error_event(cls, message: str, source: str = "") -> "EventBuilder":
        return cls(
            type=EventType.ERROR,
            payload={"message": message},
            source=source,
        )
