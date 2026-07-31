"""Formatter for code style enforcement."""
from typing import Any


class Formatter:
    """Formats code according to style rules."""

    def __init__(self):
        self._config: dict[str, Any] = {
            "max_line_length": 88,
            "indent_size": 4,
            "use_spaces": True,
        }

    def format(self, content: str) -> str:
        lines = content.split("\n")
        formatted = []
        for line in lines:
            stripped = line.rstrip()
            if stripped:
                formatted.append(stripped)
            else:
                formatted.append("")
        return "\n".join(formatted)

    def check_line_length(self, content: str, max_length: int = None) -> list[dict[str, Any]]:
        max_len = max_length or self._config["max_line_length"]
        violations = []
        for i, line in enumerate(content.split("\n"), 1):
            if len(line) > max_len:
                violations.append({
                    "line": i,
                    "length": len(line),
                    "max": max_len,
                })
        return violations

    def check_indentation(self, content: str) -> list[dict[str, Any]]:
        violations = []
        indent_size = self._config["indent_size"]
        for i, line in enumerate(content.split("\n"), 1):
            stripped = line.lstrip()
            if stripped:
                indent = len(line) - len(stripped)
                if indent % indent_size != 0:
                    violations.append({"line": i, "indent": indent, "expected_multiple": indent_size})
        return violations

    def set_config(self, key: str, value: Any) -> None:
        self._config[key] = value

    def get_config(self) -> dict[str, Any]:
        return dict(self._config)
