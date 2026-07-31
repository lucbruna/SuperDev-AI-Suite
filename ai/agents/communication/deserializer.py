from __future__ import annotations

import json
from typing import Any


class Deserializer:
    """Deserializes messages from JSON format."""

    @staticmethod
    def deserialize(data: str) -> dict[str, Any]:
        return json.loads(data)

    @staticmethod
    def dict_to_message(data: dict[str, Any]) -> dict[str, Any]:
        return dict(data)
