from __future__ import annotations

from SuperDev.data.data_models import (
    DataBatch,
    DataQualityStatus,
    DataRecord,
    DataSourceType,
    PipelineDefinition,
    PipelineRun,
    PipelineRunStatus,
    StarSchema,
)


class TestDataRecord:
    def test_defaults(self) -> None:
        record = DataRecord()
        assert record.id
        assert record.state.value == "raw"
        assert record.quality == DataQualityStatus.UNKNOWN

    def test_with_data(self) -> None:
        record = DataRecord(source="test", data={"value": 42})
        assert record.data["value"] == 42


class TestDataBatch:
    def test_defaults(self) -> None:
        batch = DataBatch()
        assert batch.batch_id
        assert batch.records == []

    def test_with_records(self) -> None:
        batch = DataBatch(source="s", records=[DataRecord(), DataRecord()])
        assert len(batch.records) == 2


class TestPipelineModels:
    def test_definition(self) -> None:
        definition = PipelineDefinition(name="p", steps=[{"type": "ingest"}])
        assert definition.status.value == "draft"

    def test_run(self) -> None:
        run = PipelineRun(pipeline_id="p1")
        assert run.status == PipelineRunStatus.PENDING


class TestStarSchema:
    def test_schema(self) -> None:
        schema = StarSchema(name="sales")
        assert schema.dimensions == []


class TestIngestionSource:
    def test_default_type(self) -> None:
        from SuperDev.data.data_models import IngestionSource

        source = IngestionSource(name="api")
        assert source.source_type == DataSourceType.API
