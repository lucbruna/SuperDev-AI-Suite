"""Core engine for version management operations."""

from typing import Any

from .branch_manager import BranchManager
from .dependency_resolver import DependencyResolver
from .models import Tag, Version
from .tag_manager import TagManager
from .version_manager import VersionManager


class VersioningEngine:
    def __init__(self):
        self.version_manager = VersionManager()
        self.tag_manager = TagManager()
        self.branch_manager = BranchManager()
        self.dependency_resolver = DependencyResolver()
        self._versions: list[Version] = []

    def create_version(self, major: int, minor: int, patch: int) -> Version:
        v = Version(major=major, minor=minor, patch=patch)
        self._versions.append(v)
        return v

    def get_latest_version(self) -> Version | None:
        if not self._versions:
            return None
        return max(self._versions, key=lambda v: v.to_tuple())

    def bump_version(self, version: Version, bump_type: str = "patch") -> Version:
        if bump_type == "major":
            new_v = version.bump_major()
        elif bump_type == "minor":
            new_v = version.bump_minor()
        else:
            new_v = version.bump_patch()
        self._versions.append(new_v)
        return new_v

    def create_tag(self, name: str, version: Version, message: str = "") -> Tag:
        return self.tag_manager.create_tag(name, str(version), message)

    def get_all_versions(self) -> list[Version]:
        return list(self._versions)

    def get_stats(self) -> dict[str, Any]:
        return {
            "versions": len(self._versions),
            "tags": self.tag_manager.count(),
            "branches": self.branch_manager.count(),
        }
