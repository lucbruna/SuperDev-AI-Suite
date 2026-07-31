from __future__ import annotations

from typing import Any


class ContextExpander:
    """Expands context entries with additional detail or derived data."""

    def __init__(self):
        self._expansion_count: int = 0

    @property
    def expansion_count(self) -> int:
        return self._expansion_count

    def expand_entry(self, entry: dict[str, Any], extra_data: dict[str, Any]) -> dict[str, Any]:
        expanded = dict(entry)
        content = dict(expanded.get("content", {}))
        content.update(extra_data)
        expanded["content"] = content
        metadata = dict(expanded.get("metadata", {}))
        metadata["expanded"] = True
        expanded["metadata"] = metadata
        self._expansion_count += 1
        return expanded

    def expand_key(self, context: dict[str, Any], key: str, value: Any) -> dict[str, Any]:
        result = dict(context)
        content = dict(result.get("content", {}))
        content[key] = value
        result["content"] = content
        result["metadata"] = dict(result.get("metadata", {}))
        result["metadata"]["expanded"] = True
        self._expansion_count += 1
        return result

    def expand_from_source(
        self, context: dict[str, Any], source_key: str, target_key: str, transformer: Any = None
    ) -> dict[str, Any]:
        content = dict(context.get("content", {}))
        if source_key not in content:
            return context
        source_value = content[source_key]
        if transformer:
            content[target_key] = transformer(source_value)
        else:
            content[target_key] = f"{source_value} (expanded)"
        result = dict(context)
        result["content"] = content
        result["metadata"] = dict(result.get("metadata", {}))
        result["metadata"]["expanded"] = True
        self._expansion_count += 1
        return result

    def reset(self) -> None:
        self._expansion_count = 0
