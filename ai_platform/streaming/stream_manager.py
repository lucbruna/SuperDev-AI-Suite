from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any

from ..providers.base_provider import BaseProvider


@dataclass
class StreamInfo:
    stream_id: str
    provider: BaseProvider
    messages: list[dict]
    config: dict[str, Any]
    created_at: float = 0.0
    cancelled: bool = False


class StreamManager:
    def __init__(self):
        self._streams: dict[str, StreamInfo] = {}

    def create_stream(self, provider: BaseProvider, messages: list[dict], config: dict[str, Any]) -> str:
        stream_id = str(uuid.uuid4())
        self._streams[stream_id] = StreamInfo(
            stream_id=stream_id,
            provider=provider,
            messages=messages,
            config=config,
            created_at=time.time(),
        )
        return stream_id

    def get_stream(self, stream_id: str) -> StreamInfo | None:
        return self._streams.get(stream_id)

    async def cancel_stream(self, stream_id: str) -> bool:
        info = self._streams.get(stream_id)
        if info:
            info.cancelled = True
            del self._streams[stream_id]
            return True
        return False

    def list_active_streams(self) -> dict[str, StreamInfo]:
        return dict(self._streams)

    def cleanup_expired(self, max_age: float = 3600) -> int:
        now = time.time()
        expired = [sid for sid, info in self._streams.items() if now - info.created_at > max_age]
        for sid in expired:
            del self._streams[sid]
        return len(expired)
