"""Manager for versioning lifecycle and configuration."""
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import Version, Branch, Tag


class VersioningManager:
    def __init__(self):
        self._versions: List[Version] = []
        self._branches: List[Branch] = []
        self._tags: List[Tag] = []
        self._history: List[Dict[str, Any]] = []

    def register_version(self, version: Version) -> None:
        self._versions.append(version)
        self._history.append({
            "action": "register_version",
            "version": str(version),
            "timestamp": datetime.utcnow().isoformat(),
        })

    def get_version(self, version_str: str) -> Optional[Version]:
        for v in self._versions:
            if str(v) == version_str:
                return v
        return None

    def list_versions(self) -> List[Version]:
        return list(self._versions)

    def add_branch(self, branch: Branch) -> None:
        self._branches.append(branch)

    def add_tag(self, tag: Tag) -> None:
        self._tags.append(tag)

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self._history)

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "versions": len(self._versions),
            "branches": len(self._branches),
            "tags": len(self._tags),
        }
