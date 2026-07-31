"""Renders template placeholders into concrete steps."""

from __future__ import annotations

import re
from typing import Any

_PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z_]\w*)\s*\}\}")


class TemplateRenderer:
    """Substitutes ``{{param}}`` placeholders inside template steps."""

    def render(self, steps: list[dict[str, Any]],
               variables: dict[str, Any]) -> list[dict[str, Any]]:
        """Returns a deep copy of steps with placeholders replaced."""
        rendered: list[dict[str, Any]] = []
        for step in steps:
            out = dict(step)
            if isinstance(out.get("action"), str):
                out["action"] = self.substitute(out["action"], variables)
            if isinstance(out.get("params"), dict):
                out["params"] = self._substitute_value(out["params"], variables)
            rendered.append(out)
        return rendered

    def substitute(self, text: str, variables: dict[str, Any]) -> str:
        """Replaces known placeholders; unknown ones are left untouched."""
        def repl(match: re.Match[str]) -> str:
            name = match.group(1)
            if name in variables:
                return str(variables[name])
            return match.group(0)
        return _PLACEHOLDER.sub(repl, text)

    def _substitute_value(self, value: Any, variables: dict[str, Any]) -> Any:
        if isinstance(value, str):
            return self.substitute(value, variables)
        if isinstance(value, dict):
            return {k: self._substitute_value(v, variables)
                    for k, v in value.items()}
        if isinstance(value, list):
            return [self._substitute_value(v, variables) for v in value]
        return value
