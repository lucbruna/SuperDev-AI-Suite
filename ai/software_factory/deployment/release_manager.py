"""Manager for release lifecycle."""
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import Release


class ReleaseManager:
    """Manages releases and versioning."""

    def __init__(self):
        self._releases: List[Release] = []

    def create_release(self, version: str, name: str, description: str = "") -> Release:
        release = Release(version=version, name=name, description=description)
        self._releases.append(release)
        return release

    def add_changelog(self, release_id: str, entry: str) -> bool:
        for release in self._releases:
            if release.release_id == release_id:
                release.changelog.append(entry)
                return True
        return False

    def mark_deployed(self, release_id: str, environment: str) -> bool:
        for release in self._releases:
            if release.release_id == release_id:
                if environment not in release.deployed_environments:
                    release.deployed_environments.append(environment)
                return True
        return False

    def get_release(self, release_id: str) -> Optional[Release]:
        for r in self._releases:
            if r.release_id == release_id:
                return r
        return None

    def get_latest(self) -> Optional[Release]:
        return self._releases[-1] if self._releases else None

    def list_releases(self) -> List[Release]:
        return list(self._releases)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_releases": len(self._releases),
            "deployed": sum(1 for r in self._releases if r.deployed_environments),
        }
