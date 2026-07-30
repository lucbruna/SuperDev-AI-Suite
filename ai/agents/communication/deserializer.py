from __future__ import annotations

import json
from typing import Any, Dict


class Deserializer:
    """Deserializes messages from JSON format."""

    @staticmethod
    def deserialize(data: str) -> Dict[str, Any]:
        return json.loads(data)

    @staticmethod
    def dict_to_message(data: Dict[str, Any]) -> Dict[str, Any]:
        return dict(data)
