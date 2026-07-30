from __future__ import annotations

import json
from typing import Any

from ..api_interfaces import IAPISerializer


class JSONSerializer(IAPISerializer):
    """JSON serializer/deserializer."""

    def serialize(self, data: Any, fmt: str = "json") -> str:
        return json.dumps(data, default=str, ensure_ascii=False, indent=2)

    def deserialize(self, data: Any, fmt: str = "json") -> Any:
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        return json.loads(data)

    def to_dict(self) -> dict[str, Any]:
        return {"serializer": "JSON"}
