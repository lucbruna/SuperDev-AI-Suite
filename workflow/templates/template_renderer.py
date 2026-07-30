from __future__ import annotations

import re
from typing import Any


class TemplateRenderer:
    """Renders templates by substituting variables."""

    def __init__(self) -> None:
        self._pattern = re.compile(r"\{\{(\w+)\}\}")

    def render(self, content: str, variables: dict[str, Any]) -> str:
        def replace(match: re.Match[str]) -> str:
            var = match.group(1)
            return str(variables.get(var, match.group(0)))
        return self._pattern.sub(replace, content)
