"""Streaming models."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class StreamStatus(Enum):
    IDLE = "idle"
    STREAMING = "streaming"
    PAUSED = "paused"
    ERROR = "error"


class EventType(Enum):
    DATA = "data"
    HEARTBEAT = "heartbeat"
    ALERT = "alert"
    CONTROL = "control"


@dataclass
class StreamTopic:
    topic_id: str
    name: str = ""
    status: StreamStatus = StreamStatus.IDLE
    message_count: int = 0
    consumer_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class StreamEvent:
    event_id: str
    topic_id: str = ""
    event_type: EventType = EventType.DATA
    payload: dict[str, Any] = field(default_factory=dict)
    partition_key: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    sequence: int = 0


@dataclass
class StreamConsumer:
    consumer_id: str
    topic_id: str = ""
    group_id: str = ""
    offset: int = 0
    status: StreamStatus = StreamStatus.IDLE
    last_commit: datetime | None = None


@dataclass
class StreamPipeline:
    pipeline_id: str
    name: str = ""
    source_topic: str = ""
    target_topic: str = ""
    transforms: list[dict[str, Any]] = field(default_factory=list)
    status: StreamStatus = StreamStatus.IDLE
    processed_count: int = 0
