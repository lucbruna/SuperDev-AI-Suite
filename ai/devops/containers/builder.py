"""Image builder."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class ImageBuilder:
    def __init__(self) -> None:
        self._builds: List[Dict[str, Any]] = []
    def build(self, dockerfile: str, context: str = ".", tags: List[str] = None) -> Dict[str, Any]:
        import uuid
        build_id = str(uuid.uuid4())[:8]
        build = {"build_id": build_id, "dockerfile": dockerfile, "context": context, "tags": tags or ["latest"], "status": "success", "duration_seconds": 45.0, "timestamp": time.time()}
        self._builds.append(build)
        return build
    def get_build(self, build_id: str) -> Dict[str, Any]:
        for b in self._builds:
            if b["build_id"] == build_id:
                return b
        return {"error": "not_found"}
    def list_builds(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._builds[-limit:]
    def count(self) -> int:
        return len(self._builds)
