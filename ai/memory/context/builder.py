from __future__ import annotations

from typing import Any, Dict, List, Optional


class ContextBuilder:
    """Builds context objects from raw source data."""

    def __init__(self):
        self._build_count: int = 0

    @property
    def build_count(self) -> int:
        return self._build_count

    def build(self, sources: List[str]) -> Dict[str, Any]:
        context: Dict[str, Any] = {
            "sources": list(sources),
            "content": {},
            "metadata": {"source_count": len(sources), "built": True},
        }
        for src in sources:
            context["content"][src] = f"<content from {src}>"
        self._build_count += 1
        return context

    def build_from_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        context = {
            "sources": list(data.keys()),
            "content": dict(data),
            "metadata": {"source_count": len(data), "built": True},
        }
        self._build_count += 1
        return context

    def merge(self, contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        merged_sources: List[str] = []
        merged_content: Dict[str, Any] = {}
        for ctx in contexts:
            merged_sources.extend(ctx.get("sources", []))
            merged_content.update(ctx.get("content", {}))
        return {
            "sources": merged_sources,
            "content": merged_content,
            "metadata": {"source_count": len(merged_sources), "merged": True},
        }

    def reset(self) -> None:
        self._build_count = 0
