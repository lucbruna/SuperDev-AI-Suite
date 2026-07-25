from __future__ import annotations

import json
from typing import Any


class BaseSerializer:
    """Base serialization utilities."""

    @staticmethod
    def to_json(data: Any, indent: int = 2) -> str:
        return json.dumps(data, indent=indent, default=str)

    @staticmethod
    def from_json(data: str) -> Any:
        return json.loads(data)

    @staticmethod
    def to_dict(data: Any) -> dict[str, Any]:
        if isinstance(data, dict):
            return data
        if hasattr(data, "model_dump"):
            return data.model_dump()
        if hasattr(data, "__dict__"):
            return {k: v for k, v in data.__dict__.items() if not k.startswith("_")}
        return {"value": data}

    @staticmethod
    def serialize_list(items: list[Any]) -> list[dict[str, Any]]:
        return [BaseSerializer.to_dict(item) for item in items]


serializer = BaseSerializer()
