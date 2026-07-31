"""CI/CD engine (Volume 37, Fase 3)."""

from __future__ import annotations

from devops_engine.cicd.build_manager import BuildManager
from devops_engine.cicd.pipeline_manager import PipelineManager
from devops_engine.cicd.release_manager import ReleaseManager
from devops_engine.devops_config import DevopsConfig
from devops_engine.devops_events import DevopsEventType, DevopsEvents
from devops_engine.devops_metrics import DevopsMetrics
from devops_engine.devops_models import (Build, Pipeline, PipelineStatus,
                                         Release)
from devops_engine.devops_security import DevopsSecurity


class CicdEngine:
    """Facade over pipelines, builds and releases."""

    def __init__(self, config: DevopsConfig | None = None,
                 events: DevopsEvents | None = None,
                 metrics: DevopsMetrics | None = None,
                 security: DevopsSecurity | None = None) -> None:
        self.config = config or DevopsConfig()
        self.events = events or DevopsEvents()
        self.metrics = metrics or DevopsMetrics()
        self.security = security or DevopsSecurity()
        self.pipelines = PipelineManager()
        self.builds = BuildManager()
        self.releases = ReleaseManager()

    def create_pipeline(self, name: str,
                        steps: list[str] | None = None) -> Pipeline:
        return self.pipelines.create(name, steps)

    def run(self, pipeline_id: str) -> bool:
        pipeline = self.pipelines.get(pipeline_id)
        if pipeline is None or pipeline.status != PipelineStatus.PENDING:
            return False
        self.pipelines.start(pipeline_id)
        self.events.publish(DevopsEventType.PIPELINE_STARTED,
                            {"pipeline_id": pipeline_id})
        build = self.builds.create(pipeline_id, commit="main")
        self.builds.succeed(build.build_id, duration=0.42)
        self.events.publish(DevopsEventType.BUILD_SUCCEEDED,
                            {"build_id": build.build_id})
        self.pipelines.succeed(pipeline_id)
        self.events.publish(DevopsEventType.PIPELINE_SUCCEEDED,
                            {"pipeline_id": pipeline_id})
        self.metrics.increment("devops.cicd.builds")
        self.metrics.increment("devops.cicd.pipelines")
        return True

    def create_build(self, pipeline_id: str, commit: str = "") -> Build:
        return self.builds.create(pipeline_id, commit)

    def release(self, version: str,
                pipeline_id: str = "") -> Release:
        return self.releases.create(version, pipeline_id)

    def deploy_release(self, release_id: str) -> bool:
        if not self.releases.deploy(release_id):
            return False
        self.events.publish(DevopsEventType.RELEASE_DEPLOYED,
                            {"release_id": release_id})
        return True

    def rollback_release(self, release_id: str,
                         actor: str = "admin") -> bool:
        if not self.security.approve(actor):
            self.security.audit_deny(actor, release_id)
            return False
        if not self.releases.rollback(release_id):
            return False
        self.events.publish(DevopsEventType.RELEASE_ROLLED_BACK,
                            {"release_id": release_id, "actor": actor})
        return True

    def stats(self) -> dict[str, int]:
        return {
            "pipelines": self.pipelines.count(),
            "builds": self.builds.count(),
            "releases": self.releases.count(),
        }
