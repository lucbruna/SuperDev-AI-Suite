from __future__ import annotations

from typing import Any, Dict, List, Optional


class ContextLoader:
    """Loads context data from various sources."""

    def __init__(self):
        self._load_count: int = 0

    @property
    def load_count(self) -> int:
        return self._load_count

    def load_text(self, text: str, source_name: str = "inline") -> Dict[str, Any]:
        self._load_count += 1
        return {
            "source": source_name,
            "type": "text",
            "content": text,
            "metadata": {"length": len(text)},
        }

    def load_dict(self, data: Dict[str, Any], source_name: str = "dict") -> Dict[str, Any]:
        self._load_count += 1
        return {
            "source": source_name,
            "type": "dict",
            "content": dict(data),
            "metadata": {"keys": list(data.keys())},
        }

    def load_list(self, items: List[Any], source_name: str = "list") -> Dict[str, Any]:
        self._load_count += 1
        return {
            "source": source_name,
            "type": "list",
            "content": list(items),
            "metadata": {"length": len(items)},
        }

    def load_batch(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for src in sources:
            st = src.get("type", "text")
            if st == "text":
                results.append(self.load_text(src.get("content", ""), src.get("name", "inline")))
            elif st == "dict":
                results.append(self.load_dict(src.get("data", {}), src.get("name", "dict")))
            elif st == "list":
                results.append(self.load_list(src.get("items", []), src.get("name", "list")))
        return results

    def reset(self) -> None:
        self._load_count = 0
