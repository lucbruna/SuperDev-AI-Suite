from __future__ import annotations

from workflow.pipelines.pipeline_models import Pipeline, PipelineStatus
from workflow.pipelines.pipeline_builder import PipelineBuilder
from workflow.pipelines.pipeline_context import PipelineContext


class TestPipelines:
    def test_pipeline_builder(self) -> None:
        builder = PipelineBuilder()
        pipeline = builder.build("test")
        assert pipeline.name == "test"
        assert pipeline.status == PipelineStatus.IDLE

    def test_pipeline_context(self) -> None:
        ctx = PipelineContext({"key": "value"})
        assert ctx.get("key") == "value"
        ctx.set("key2", "value2")
        assert ctx.get("key2") == "value2"

    def test_pipeline_status_transitions(self) -> None:
        p = Pipeline(name="test")
        assert p.status == PipelineStatus.IDLE
        p.status = PipelineStatus.RUNNING
        assert p.status == PipelineStatus.RUNNING
        p.status = PipelineStatus.COMPLETED
        assert p.status == PipelineStatus.COMPLETED
