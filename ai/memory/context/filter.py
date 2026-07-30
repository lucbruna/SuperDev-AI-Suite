from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional


class ContextFilter:
    """Filters context items by various criteria."""

    def __init__(self):
        self._filter_count: int = 0

    @property
    def filter_count(self) -> int:
        return self._filter_count

    def filter_by_key(self, context: Dict[str, Any], include_keys: List[str]) -> Dict[str, Any]:
        content = context.get("content", {})
        filtered = {k: v for k, v in content.items() if k in include_keys}
        result = dict(context)
        result["content"] = filtered
        result["metadata"] = dict(result.get("metadata", {}))
        result["metadata"]["filtered"] = True
        self._filter_count += 1
        return result

    def filter_by_type(self, context: Dict[str, Any], include_types: List[str]) -> Dict[str, Any]:
        content = context.get("content", {})
        filtered: Dict[str, Any] = {}
        for k, v in content.items():
            if isinstance(v, dict) and v.get("type") in include_types:
                filtered[k] = v
            elif isinstance(v, str) and "type" not in include_types:
                filtered[k] = v
        result = dict(context)
        result["content"] = filtered
        result["metadata"] = dict(result.get("metadata", {}))
        result["metadata"]["filtered_by_type"] = True
        self._filter_count += 1
        return result

    def filter_by_predicate(
        self, context: Dict[str, Any], predicate: Callable[[str, Any], bool]
    ) -> Dict[str, Any]:
        content = context.get("content", {})
        filtered = {k: v for k, v in content.items() if predicate(k, v)}
        result = dict(context)
        result["content"] = filtered
        result["metadata"] = dict(result.get("metadata", {}))
        result["metadata"]["filtered_by_predicate"] = True
        self._filter_count += 1
        return result

    def filter_items(
        self, items: List[Dict[str, Any]], key: str, value: Any
    ) -> List[Dict[str, Any]]:
        self._filter_count += 1
        return [item for item in items if item.get(key) == value]

    def reset(self) -> None:
        self._filter_count = 0
