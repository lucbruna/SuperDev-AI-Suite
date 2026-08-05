"""AIOS Procedural Memory — named reusable procedures.

Stores named procedure definitions (step lists) that agents and
workflows can reference, e.g. "render_video", "publish_campaign".
"""

from __future__ import annotations

import time
import uuid
from typing import Any


class ProceduralMemory:
    """Store of named procedures (recipes)."""

    def __init__(self, max_procedures: int = 5_000) -> None:
        self._procedures: dict[str, dict[str, Any]] = {}
        self._max = max_procedures

    def store(self, content: Any, **meta: Any) -> dict[str, Any]:
        name = meta.get("name")
        if name is None:
            raise ValueError("procedural store requires meta 'name'")
        steps = content if isinstance(content, list) else meta.get("steps", [])
        procedure = {
            "record_id": f"proc-{uuid.uuid4().hex[:10]}",
            "name": name,
            "steps": list(steps),
            "description": meta.get("description", ""),
            "tags": list(meta.get("tags", [])),
            "timestamp": time.time(),
        }
        self._procedures[name] = procedure
        if len(self._procedures) > self._max:
            oldest = min(self._procedures, key=lambda k: self._procedures[k]["timestamp"])
            del self._procedures[oldest]
        return procedure

    def recall(self, query: Any = None, limit: int = 5, **filters: Any) -> list[dict[str, Any]]:
        tags = set(filters.get("tags", []))
        name = filters.get("name")
        query_str = str(query).lower() if query is not None else ""
        matches = []
        for procedure in self._procedures.values():
            if name is not None and procedure["name"] != name:
                continue
            if tags and not tags.issubset(set(procedure["tags"])):
                continue
            haystack = f"{procedure['name']} {procedure.get('description', '')}".lower()
            if query_str and query_str not in haystack:
                continue
            matches.append(procedure)
            if len(matches) >= limit:
                break
        return matches

    def forget(self, record_id: str) -> bool:
        before = len(self._procedures)
        self._procedures = {k: v for k, v in self._procedures.items() if v["record_id"] != record_id}
        return len(self._procedures) < before

    def clear(self) -> None:
        self._procedures.clear()

    def stats(self) -> dict[str, Any]:
        return {"procedures": len(self._procedures), "max": self._max}

    def snapshot(self) -> dict[str, Any]:
        return {"procedures": len(self._procedures), "max": self._max}
