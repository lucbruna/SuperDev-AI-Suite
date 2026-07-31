"""Message serialization."""

from __future__ import annotations

import json
from typing import Any


class MessageSerializer:
    """Serializes and deserializes message payloads."""

    def serialize(self, payload: dict[str, Any]) -> bytes:
        return json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")

    def deserialize(self, data: bytes) -> dict[str, Any]:
        return json.loads(data.decode("utf-8"))

    def roundtrip(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.deserialize(self.serialize(payload))
