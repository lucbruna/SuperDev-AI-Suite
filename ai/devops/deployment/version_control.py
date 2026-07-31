"""Version control."""
from __future__ import annotations
from typing import Any, Dict, List

class VersionControl:
    def __init__(self) -> None:
        self._versions: Dict[str, Dict[str, Any]] = {}
    def tag(self, version: str, commit: str, message: str = "") -> Dict[str, Any]:
        tag = {"version": version, "commit": commit, "message": message}
        self._versions[version] = tag
        return tag
    def get(self, version: str) -> Dict[str, Any]:
        return self._versions.get(version, {"error": "not_found"})
    def list_tags(self) -> List[Dict[str, Any]]:
        return list(self._versions.values())
    def latest(self) -> str:
        return list(self._versions.keys())[-1] if self._versions else ""
    def count(self) -> int:
        return len(self._versions)
