"""Template rendering for generated payloads."""

from __future__ import annotations

import re
from typing import Any

_TOKEN = re.compile(r"\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}")


class TemplateRenderer:
    """Renders simple {{ field.path }} templates against a data record."""

    def render(self, template: str, data: dict[str, Any]) -> str:
        def resolve(match: re.Match[str]) -> str:
            path = match.group(1).split(".")
            value: Any = data
            for part in path:
                if not isinstance(value, dict) or part not in value:
                    return ""
                value = value[part]
            return str(value)

        return _TOKEN.sub(resolve, template)

    def has_tokens(self, template: str) -> bool:
        return bool(_TOKEN.search(template))
