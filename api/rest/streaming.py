from __future__ import annotations

import json
import time
from typing import Any, AsyncIterator

from ..api_models import APIResponse


async def stream_json(data_generator: AsyncIterator[Any]) -> AsyncIterator[str]:
    """Yield NDJSON chunks from an async data generator."""
    async for item in data_generator:
        yield json.dumps(item, default=str, ensure_ascii=False) + "\n"


async def stream_text(data_generator: AsyncIterator[str]) -> AsyncIterator[str]:
    """Yield text chunks from an async data generator."""
    async for chunk in data_generator:
        yield chunk


class StreamingResponse:
    """Wraps an async generator into a streaming APIResponse."""

    def __init__(
        self,
        generator: AsyncIterator[Any],
        content_type: str = "application/x-ndjson",
        status: int = 200,
    ) -> None:
        self._generator = generator
        self._content_type = content_type
        self._status = status
        self._headers: dict[str, str] = {
            "content-type": content_type,
            "cache-control": "no-cache",
            "x-accel-buffering": "no",
        }

    @property
    def status(self) -> int:
        return self._status

    @property
    def headers(self) -> dict[str, str]:
        return dict(self._headers)

    async def iter_body(self) -> AsyncIterator[str]:
        async for chunk in self._generator:
            if isinstance(chunk, str):
                yield chunk
            else:
                yield json.dumps(chunk, default=str, ensure_ascii=False) + "\n"

    def to_response(self) -> APIResponse:
        return APIResponse(
            status_code=self._status,
            headers=self._headers,
            content_type=self._content_type,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "streaming": True,
            "content_type": self._content_type,
            "status": self._status,
        }


class SSESession:
    """Server-Sent Events session helper."""

    def __init__(self, event_source: AsyncIterator[dict[str, Any]]) -> None:
        self._source = event_source
        self._last_id: int = 0

    async def iter_events(self) -> AsyncIterator[str]:
        async for event_data in self._source:
            self._last_id += 1
            event_type = event_data.get("event", "message")
            data = json.dumps(event_data.get("data", event_data), default=str, ensure_ascii=False)
            yield f"id: {self._last_id}\nevent: {event_type}\ndata: {data}\n\n"

    async def send_comment(self, comment: str) -> str:
        return f": {comment}\n\n"

    async def send_retry(self, ms: int) -> str:
        return f"retry: {ms}\n\n"

    def to_dict(self) -> dict[str, Any]:
        return {"sse": True, "last_id": self._last_id}
