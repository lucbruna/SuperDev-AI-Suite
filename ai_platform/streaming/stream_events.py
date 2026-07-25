from __future__ import annotations
from typing import Any, Optional
from enum import Enum
from dataclasses import dataclass, field, asdict
import json


class StreamEventType(str, Enum):
    START = "start"
    CHUNK = "chunk"
    END = "end"
    ERROR = "error"
    CANCEL = "cancel"


@dataclass
class StreamEvent:
    event: StreamEventType
    data: dict[str, Any] = field(default_factory=dict)
    stream_id: str = ""
    timestamp: str = ""

    def to_sse(self) -> str:
        payload = {
            "event": self.event.value,
            "data": self.data,
            "stream_id": self.stream_id,
            "timestamp": self.timestamp,
        }
        lines = []
        raw = json.dumps(payload, default=str)
        for line in raw.split("\n"):
            lines.append(f"data: {line}")
        lines.append("")
        lines.append("")
        return "\n".join(lines)

    @classmethod
    def start(cls, stream_id: str, metadata: Optional[dict] = None) -> "StreamEvent":
        import time
        return cls(
            event=StreamEventType.START,
            data=metadata or {},
            stream_id=stream_id,
            timestamp=str(time.time()),
        )

    @classmethod
    def chunk(cls, stream_id: str, content: str, index: int = 0) -> "StreamEvent":
        import time
        return cls(
            event=StreamEventType.CHUNK,
            data={"content": content, "index": index},
            stream_id=stream_id,
            timestamp=str(time.time()),
        )

    @classmethod
    def end(cls, stream_id: str, usage: Optional[dict] = None) -> "StreamEvent":
        import time
        return cls(
            event=StreamEventType.END,
            data=usage or {},
            stream_id=stream_id,
            timestamp=str(time.time()),
        )

    @classmethod
    def error(cls, stream_id: str, message: str) -> "StreamEvent":
        import time
        return cls(
            event=StreamEventType.ERROR,
            data={"error": message},
            stream_id=stream_id,
            timestamp=str(time.time()),
        )

    @classmethod
    def cancel(cls, stream_id: str) -> "StreamEvent":
        import time
        return cls(
            event=StreamEventType.CANCEL,
            data={},
            stream_id=stream_id,
            timestamp=str(time.time()),
        )
