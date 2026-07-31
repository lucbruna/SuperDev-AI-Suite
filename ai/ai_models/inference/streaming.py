"""Streaming support."""
from __future__ import annotations
from typing import Any, Callable, Dict, Generator, List

class StreamingManager:
    def __init__(self) -> None:
        self._streams: Dict[str, List[Dict[str, Any]]] = {}
        self._handlers: Dict[str, Callable] = {}
    def create_stream(self, stream_id: str) -> None:
        self._streams[stream_id] = []
    def add_chunk(self, stream_id: str, chunk: Dict[str, Any]) -> None:
        self._streams.setdefault(stream_id, []).append(chunk)
    def get_chunks(self, stream_id: str) -> List[Dict[str, Any]]:
        return list(self._streams.get(stream_id, []))
    def complete_stream(self, stream_id: str) -> str:
        chunks = self._streams.get(stream_id, [])
        return "".join(c.get("content", "") for c in chunks)
    def set_handler(self, stream_id: str, handler: Callable) -> None:
        self._handlers[stream_id] = handler
    def process_stream(self, stream_id: str, data: Any) -> Any:
        handler = self._handlers.get(stream_id)
        if handler:
            return handler(data)
        return data
    def list_streams(self) -> List[str]:
        return list(self._streams.keys())
    def delete_stream(self, stream_id: str) -> bool:
        if stream_id in self._streams:
            del self._streams[stream_id]
            self._handlers.pop(stream_id, None)
            return True
        return False
    def chunk_count(self, stream_id: str) -> int:
        return len(self._streams.get(stream_id, []))
