"""
API Versioning - Version management
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class APIVersion:
    version: str
    status: str = "active"
    base_path: str = ""
    release_date: Optional[datetime] = None
    deprecated: bool = False
    sunset_date: Optional[datetime] = None
    changelog: List[str] = field(default_factory=list)


class VersionManager:
    def __init__(self):
        self.versions: Dict[str, APIVersion] = {}
        self.default_version: str = "v1"

    def register_version(self, version: str, base_path: str = "", **kwargs) -> APIVersion:
        api_version = APIVersion(version=version, base_path=base_path, release_date=datetime.now(), **kwargs)
        self.versions[version] = api_version
        return api_version

    def get_version(self, version: str) -> Optional[APIVersion]:
        return self.versions.get(version)

    def deprecate_version(self, version: str) -> bool:
        v = self.versions.get(version)
        if v:
            v.deprecated = True
            v.status = "deprecated"
            return True
        return False

    def set_default(self, version: str) -> bool:
        if version in self.versions:
            self.default_version = version
            return True
        return False

    def get_active(self) -> List[APIVersion]:
        return [v for v in self.versions.values() if v.status == "active"]

    def list_all(self) -> List[APIVersion]:
        return list(self.versions.values())

    def count(self) -> int:
        return len(self.versions)
