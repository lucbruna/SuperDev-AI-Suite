from __future__ import annotations

import json
from typing import Any, Dict


class Serializer:
    """Serializes messages to JSON format."""

    @staticmethod
    def serialize(data: Dict[str, Any]) -> str:
        return json.dumps(data, default=str)

    @staticmethod
    def message_to_dict(msg: Dict[str, Any]) -> Dict[str, Any]:
        return dict(msg)

    @staticmethod
    def envelope_to_dict(env: Any) -> Dict[str, Any]:
        return env.to_dict() if hasattr(env, "to_dict") else {"data": str(env)}
