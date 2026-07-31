"""CI/CD build management (Volume 37, Fase 3)."""

from __future__ import annotations

from devops_engine.devops_models import Build, BuildStatus
from devops_engine.devops_protocols import new_id, now


class BuildManager:
    """Tracks builds executed by pipelines."""

    def __init__(self) -> None:
        self._builds: dict[str, Build] = {}

    def create(self, pipeline_id: str, commit: str = "") -> Build:
        build = Build(
            build_id=new_id("build"),
            pipeline_id=pipeline_id,
            commit=commit,
            status=BuildStatus.PENDING,
            created_at=now(),
        )
        self._builds[build.build_id] = build
        return build

    def succeed(self, build_id: str, duration: float = 0.0) -> bool:
        build = self._builds.get(build_id)
        if build is None:
            return False
        build.status = BuildStatus.SUCCEEDED
        build.duration = float(duration)
        return True

    def fail(self, build_id: str) -> bool:
        build = self._builds.get(build_id)
        if build is None:
            return False
        build.status = BuildStatus.FAILED
        return True

    def get(self, build_id: str) -> Build | None:
        return self._builds.get(build_id)

    def list(self) -> list[Build]:
        return list(self._builds.values())

    def count(self) -> int:
        return len(self._builds)
