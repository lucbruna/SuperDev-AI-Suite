"""Tests for the CI/CD subpackage (Volume 37, Fase 3)."""

from __future__ import annotations

import pytest

from devops_engine.cicd import CicdEngine
from devops_engine.devops_events import DevopsEventType, DevopsEvents
from devops_engine.devops_models import (BuildStatus, PipelineStatus,
                                         ReleaseStatus)


@pytest.fixture()
def cicd() -> CicdEngine:
    return CicdEngine()


class TestPipelineManager:
    def test_lifecycle(self, cicd: CicdEngine) -> None:
        pipeline = cicd.pipelines.create("ci", ["test", "deploy"])
        assert pipeline.status == PipelineStatus.PENDING
        assert pipeline.steps == ["test", "deploy"]
        assert cicd.pipelines.start(pipeline.pipeline_id) is True
        assert pipeline.status == PipelineStatus.RUNNING
        assert cicd.pipelines.succeed(pipeline.pipeline_id) is True
        assert pipeline.status == PipelineStatus.SUCCEEDED

    def test_cancel(self, cicd: CicdEngine) -> None:
        pipeline = cicd.pipelines.create("ci")
        assert cicd.pipelines.cancel(pipeline.pipeline_id) is True
        assert pipeline.status == PipelineStatus.CANCELLED

    def test_fail(self, cicd: CicdEngine) -> None:
        pipeline = cicd.pipelines.create("ci")
        assert cicd.pipelines.fail(pipeline.pipeline_id) is True
        assert pipeline.status == PipelineStatus.FAILED


class TestBuildManager:
    def test_succeed(self, cicd: CicdEngine) -> None:
        build = cicd.builds.create("p1", commit="abc123")
        assert build.status == BuildStatus.PENDING
        assert cicd.builds.succeed(build.build_id, duration=1.5) is True
        assert build.status == BuildStatus.SUCCEEDED
        assert build.duration == 1.5

    def test_fail(self, cicd: CicdEngine) -> None:
        build = cicd.builds.create("p1")
        assert cicd.builds.fail(build.build_id) is True
        assert build.status == BuildStatus.FAILED


class TestReleaseManager:
    def test_deploy_rollback(self, cicd: CicdEngine) -> None:
        release = cicd.releases.create("1.0.0")
        assert release.status == ReleaseStatus.DRAFT
        assert cicd.releases.deploy(release.release_id) is True
        assert release.status == ReleaseStatus.DEPLOYED
        assert cicd.releases.rollback(release.release_id) is True
        assert release.status == ReleaseStatus.ROLLED_BACK


class TestCicdEngine:
    def test_run_pipeline(self, cicd: CicdEngine) -> None:
        events = DevopsEvents()
        cicd.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.PIPELINE_SUCCEEDED, seen.append)
        pipeline = cicd.create_pipeline("ci", ["test", "build", "deploy"])
        assert cicd.run(pipeline.pipeline_id) is True
        assert pipeline.status == PipelineStatus.SUCCEEDED
        assert len(seen) == 1
        assert cicd.metrics.count("devops.cicd.builds") == 1

    def test_run_only_once(self, cicd: CicdEngine) -> None:
        pipeline = cicd.create_pipeline("ci")
        assert cicd.run(pipeline.pipeline_id) is True
        assert cicd.run(pipeline.pipeline_id) is False

    def test_run_missing(self, cicd: CicdEngine) -> None:
        assert cicd.run("nope") is False

    def test_create_build(self, cicd: CicdEngine) -> None:
        pipeline = cicd.create_pipeline("ci")
        build = cicd.create_build(pipeline.pipeline_id, "feature-x")
        assert build.commit == "feature-x"
        assert cicd.builds.count() == 1

    def test_deploy_release(self, cicd: CicdEngine) -> None:
        release = cicd.release("2.0.0")
        assert cicd.deploy_release(release.release_id) is True
        assert release.status == ReleaseStatus.DEPLOYED

    def test_rollback_release_requires_approval(self, cicd: CicdEngine) -> None:
        release = cicd.release("2.0.0")
        cicd.deploy_release(release.release_id)
        assert cicd.rollback_release(release.release_id, "guest") is False
        assert cicd.rollback_release(release.release_id, "admin") is True
        assert release.status == ReleaseStatus.ROLLED_BACK

    def test_stats(self, cicd: CicdEngine) -> None:
        pipeline = cicd.create_pipeline("ci")
        cicd.run(pipeline.pipeline_id)
        cicd.release("1.0.0")
        assert cicd.stats()["pipelines"] == 1
        assert cicd.stats()["builds"] == 1
        assert cicd.stats()["releases"] == 1
