"""Release management for CI/CD (Volume 37, Fase 3)."""

from __future__ import annotations

from devops_engine.devops_models import Release, ReleaseStatus
from devops_engine.devops_protocols import new_id, now


class ReleaseManager:
    """Tracks released versions and rollbacks."""

    def __init__(self) -> None:
        self._releases: dict[str, Release] = {}

    def create(self, version: str, pipeline_id: str = "") -> Release:
        release = Release(
            release_id=new_id("release"),
            pipeline_id=pipeline_id,
            version=version,
            status=ReleaseStatus.DRAFT,
        )
        self._releases[release.release_id] = release
        return release

    def deploy(self, release_id: str) -> bool:
        release = self._releases.get(release_id)
        if release is None:
            return False
        release.status = ReleaseStatus.DEPLOYED
        release.deployed_at = now()
        return True

    def rollback(self, release_id: str) -> bool:
        release = self._releases.get(release_id)
        if release is None:
            return False
        release.status = ReleaseStatus.ROLLED_BACK
        return True

    def get(self, release_id: str) -> Release | None:
        return self._releases.get(release_id)

    def list(self) -> list[Release]:
        return list(self._releases.values())

    def count(self) -> int:
        return len(self._releases)
