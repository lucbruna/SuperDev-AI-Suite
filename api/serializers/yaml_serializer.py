from __future__ import annotations

from typing import Any

from ..api_interfaces import IAPISerializer


class YAMLSerializer(IAPISerializer):
    """Simple YAML-like serializer (standard library only — writes simplified YAML)."""

    def serialize(self, data: Any, fmt: str = "yaml") -> str:
        return self._to_yaml(data, 0)

    def _to_yaml(self, value: Any, indent: int) -> str:
        prefix = "  " * indent
        if isinstance(value, dict):
            lines: list[str] = []
            for key, val in value.items():
                if isinstance(val, (dict, list)):
                    lines.append(f"{prefix}{key}:")
                    lines.append(self._to_yaml(val, indent + 1))
                else:
                    lines.append(f"{prefix}{key}: {self._yaml_value(val)}")
            return "\n".join(lines)
        if isinstance(value, (list, tuple)):
            items: list[str] = []
            for item in value:
                if isinstance(item, (dict, list)):
                    items.append(f"{prefix}-")
                    items.append(self._to_yaml(item, indent + 1))
                else:
                    items.append(f"{prefix}- {self._yaml_value(item)}")
            return "\n".join(items)
        return self._yaml_value(value)

    def _yaml_value(self, value: Any) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if value is None:
            return "null"
        if isinstance(value, str):
            if any(c in value for c in ":{}[]&*?|>!%@`\n"):
                return f"'{value}'"
            return value
        return str(value)

    def deserialize(self, data: Any, fmt: str = "yaml") -> Any:
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        lines = data.strip().split("\n")
        return self._parse_yaml(lines, 0)[0] if lines else {}

    def _parse_yaml(self, lines: list[str], start: int) -> tuple[Any, int]:
        if start >= len(lines):
            return {}, start
        line = lines[start].strip()
        if not line:
            return {}, start + 1

        if line.startswith("- "):
            items: list[Any] = []
            i = start
            while i < len(lines):
                stripped = lines[i].strip()
                if not stripped.startswith("- "):
                    break
                val_text = stripped[2:].strip()
                if val_text == "":
                    child_val, i = self._parse_yaml(lines, i + 1)
                    items.append(child_val)
                else:
                    items.append(val_text)
                    i += 1
            return items, i

        if ":" in line:
            result: dict[str, Any] = {}
            i = start
            while i < len(lines):
                stripped = lines[i].strip()
                if not stripped:
                    i += 1
                    continue
                if ":" not in stripped:
                    break
                colon_pos = stripped.index(":")
                key = stripped[:colon_pos].strip()
                val_text = stripped[colon_pos + 1:].strip()
                if val_text == "":
                    child_val, i = self._parse_yaml(lines, i + 1)
                    result[key] = child_val
                else:
                    result[key] = val_text
                    i += 1
            return result, i

        return line, start + 1

    def to_dict(self) -> dict[str, Any]:
        return {"serializer": "YAML"}
