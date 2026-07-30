from __future__ import annotations

import json
from typing import Any, AsyncIterator


class GrpcSerializer:
    """JSON-based serializer acting as a protobuf replacement for gRPC."""

    @staticmethod
    def serialize_message(obj: Any) -> bytes:
        return json.dumps(obj, default=str, ensure_ascii=False).encode("utf-8")

    @staticmethod
    def deserialize_message(data: bytes, type_hint: str = "") -> dict[str, Any]:
        return json.loads(data.decode("utf-8"))

    @staticmethod
    async def serialize_stream(async_iter: AsyncIterator[Any]) -> AsyncIterator[bytes]:
        async for item in async_iter:
            yield GrpcSerializer.serialize_message(item)

    @staticmethod
    async def deserialize_stream(byte_iter: AsyncIterator[bytes]) -> AsyncIterator[dict[str, Any]]:
        async for chunk in byte_iter:
            yield GrpcSerializer.deserialize_message(chunk)

    @staticmethod
    def to_dict() -> dict[str, Any]:
        return {"serializer": "GrpcSerializer (JSON)", "format": "json"}
