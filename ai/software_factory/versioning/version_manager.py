"""Manager for version operations."""
from typing import List, Dict, Any, Optional
from .models import Version


class VersionManager:
    def __init__(self):
        self._versions: List[Version] = []

    def register(self, version: Version) -> None:
        self._versions.append(version)

    def get_all(self) -> List[Version]:
        return list(self._versions)

    def get_latest(self) -> Optional[Version]:
        return max(self._versions, key=lambda v: v.to_tuple()) if self._versions else None

    def get_by_major(self, major: int) -> List[Version]:
        return [v for v in self._versions if v.major == major]

    def compare(self, v1: Version, v2: Version) -> int:
        t1, t2 = v1.to_tuple(), v2.to_tuple()
        return (t1 > t2) - (t1 < t2)

    def is_compatible(self, current: Version, required: Version) -> bool:
        return current.major == required.major and current >= required

    def count(self) -> int:
        return len(self._versions)
