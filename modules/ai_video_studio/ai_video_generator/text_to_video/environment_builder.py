"""Environment builder — build environments from scene descriptions."""
from __future__ import annotations

import re
from typing import Any


class EnvironmentBuilder:
    """Maps scene words to an environment with props and atmosphere."""

    _KNOWN = {
        "forest": {"props": ["trees", "moss", "rocks"], "atmosphere": "calm"},
        "city": {"props": ["buildings", "cars", "lights"], "atmosphere": "busy"},
        "beach": {"props": ["sand", "waves", "shells"], "atmosphere": "relaxed"},
        "space": {"props": ["stars", "planets", "nebula"], "atmosphere": "vast"},
        "mountain": {"props": ["peaks", "snow", "cliffs"], "atmosphere": "grand"},
    }

    def build(self, description: str) -> dict[str, Any]:
        for keyword, env in self._KNOWN.items():
            if re.search(rf"\b{keyword}\b", description, re.IGNORECASE):
                return {"type": keyword, **{k: list(v) for k, v in env.items()}}
        return {"type": "generic", "props": [], "atmosphere": "neutral"}

    def add_prop(self, environment: dict[str, Any], prop: str) -> None:
        environment.setdefault("props", []).append(prop)
