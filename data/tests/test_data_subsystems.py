from __future__ import annotations

import pytest

from SuperDev.data.data_engine import DataEngine


class TestIngestion:
    @pytest.mark.asyncio
    async def test_ingest_and_register_source(self, engine: DataEngine) -> None:
        source = engine.ingestion.register_source("api-source")
        assert source.source_type.value == "api"
        batch = await engine.ingestion.ingest("api-source", {"count": 5})
        assert len(batch.records) == 5
        assert engine.ingestion.get_batch(batch.batch_id) is batch


class TestProcessing:
    @pytest.mark.asyncio
    async def test_process_cleans_and_dedupes(self, engine: DataEngine) -> None:
        from SuperDev.data.data_models import DataBatch, DataRecord

        records = [
            DataRecord(source="s", data={"id": "a", "value": " X "}),
            DataRecord(source="s", data={"id": "a", "value": None}),
        ]
        batch = DataBatch(source="s", records=records)
        processed = await engine.processing.process_batch(batch)
        # None-value cleaned out and duplicate removed
        assert len(processed.records) == 1
        assert processed.records[0].data["value"] == "x"  # normalized


class TestPipelines:
    @pytest.mark.asyncio
    async def test_run_pipeline(self, engine: DataEngine) -> None:
        definition = engine.pipelines.create_pipeline(
            "simple",
            steps=[{"type": "notify", "message": "hi"}],
        )
        run = await engine.pipelines.run(definition.pipeline_id)
        assert run.status.value == "succeeded"
        assert engine.pipelines.get_run(run.run_id) is run


class TestWarehouse:
    @pytest.mark.asyncio
    async def test_star_schema_and_insert(self, engine: DataEngine) -> None:
        from SuperDev.data.data_models import DataRecord

        schema = engine.warehouse.create_star_schema("sales")
        records = [DataRecord(source="s", data={"revenue": 100})]
        inserted = await engine.warehouse.insert(schema.fact.name, records)
        assert inserted == 1
        assert engine.warehouse.table_stats(schema.fact.name)["rows"] == 1


class TestLake:
    @pytest.mark.asyncio
    async def test_zones_and_promote(self, engine: DataEngine) -> None:
        engine.lake.put("raw", "file1", b"data")
        promoted = engine.lake.promote("file1", "raw", "processed")
        assert promoted is not None
        assert promoted.zone == "processed"
        assert engine.lake.get("raw", "file1") is None


class TestEtl:
    @pytest.mark.asyncio
    async def test_run_job(self, engine: DataEngine) -> None:
        job = engine.etl.create_job(
            "etl1",
            extract={"source": "demo", "count": 3},
            transform={"value": "double"},
            load={"table": "target"},
        )
        result = await engine.etl.run_job(job.job_id)
        assert result["status"] == "succeeded"
        assert result["rows"] == 3


class TestAnalytics:
    @pytest.mark.asyncio
    async def test_descriptive(self, engine: DataEngine) -> None:
        from SuperDev.data.data_models import DataRecord

        records = [DataRecord(source="s", data={"value": v}) for v in [1, 2, 3, 4]]
        analysis = await engine.analytics.analyze("descriptive", records, {"field": "value"})
        assert analysis.results["mean"] == 2.5

    @pytest.mark.asyncio
    async def test_correlation(self, engine: DataEngine) -> None:
        from SuperDev.data.data_models import DataRecord

        records = [DataRecord(source="s", data={"x": i, "y": i * 2}) for i in range(1, 6)]
        analysis = await engine.analytics.analyze("correlation", records, {"x": "x", "y": "y"})
        assert abs(analysis.results["correlation"] - 1.0) < 0.001


class TestBI:
    @pytest.mark.asyncio
    async def test_kpi(self, engine: DataEngine) -> None:
        kpi = engine.bi.create_kpi("Deploy Time", "deploy_time", target=30)
        assert engine.bi.update_kpi(kpi.kpi_id, 35)
        status = engine.bi.kpi_status(kpi)
        assert status["status"] == "on_track"
        assert engine.bi.update_kpi(kpi.kpi_id, 20)
        assert engine.bi.kpi_status(kpi)["status"] == "behind"

    @pytest.mark.asyncio
    async def test_dashboard(self, engine: DataEngine) -> None:
        dashboard = engine.bi.create_dashboard("Exec", owner="admin")
        assert engine.bi.add_widget(dashboard.dashboard_id, "Revenue", "chart")
        assert len(dashboard.widgets) == 1


class TestMachineLearning:
    @pytest.mark.asyncio
    async def test_train_deploy_predict(self, engine: DataEngine) -> None:
        model = engine.machine_learning.register_model("model-a")
        run = await engine.machine_learning.train(model.model_id, "dataset-a")
        assert run.status == "completed"
        assert engine.machine_learning.deploy(model.model_id)
        prediction = engine.machine_learning.predict(model.model_id, {"f1": 10, "f2": 20})
        assert prediction["prediction"] == 15.0

    @pytest.mark.asyncio
    async def test_feature_scaling(self, engine: DataEngine) -> None:
        scaled = engine.machine_learning.scale([0, 5, 10])
        assert scaled == [0.0, 0.5, 1.0]


class TestForecasting:
    @pytest.mark.asyncio
    async def test_forecast(self, engine: DataEngine) -> None:
        result = await engine.forecasting.forecast([10, 12, 11, 13], horizon=4)
        assert len(result.values) == 4

    @pytest.mark.asyncio
    async def test_anomalies(self, engine: DataEngine) -> None:
        alerts = engine.forecasting.detect_anomalies([1, 1, 1, 50, 1, 1], threshold=2.0)
        assert len(alerts) >= 1


class TestReporting:
    @pytest.mark.asyncio
    async def test_create_and_render(self, engine: DataEngine) -> None:
        report = await engine.reporting.create_report("Q3 Report", kind="financial",
                                                      data={"revenue": 1000})
        rendered = engine.reporting.render(report)
        assert "# Q3 Report" in rendered or "Q3 Report" in rendered


class TestVisualization:
    @pytest.mark.asyncio
    async def test_chart_spec(self, engine: DataEngine) -> None:
        spec = engine.visualization.render_chart("bar", {"a": 1, "b": 2}, title="T")
        assert spec["type"] == "bar"

    @pytest.mark.asyncio
    async def test_gauge_chart(self, engine: DataEngine) -> None:
        spec = engine.visualization.render_chart("gauge", {"performance": 75, "max": 100})
        assert spec["type"] == "gauge"
        assert spec["value"] == 75.0
        assert spec["max"] == 100.0

    @pytest.mark.asyncio
    async def test_funnel_chart(self, engine: DataEngine) -> None:
        spec = engine.visualization.render_chart("funnel", {"visit": 1000, "signup": 200})
        assert spec["type"] == "funnel"
        assert len(spec["stages"]) == 2
        assert spec["total"] == 1000.0


class TestGovernance:
    @pytest.mark.asyncio
    async def test_policy_evaluation(self, engine: DataEngine) -> None:
        policy = engine.governance.create_policy(
            "restrict",
            rules=[{"field": "region", "allowed": ["US"]}],
        )
        assert await engine.governance.evaluate_policy(policy.policy_id, {"region": "US"})
        assert not await engine.governance.evaluate_policy(policy.policy_id, {"region": "EU"})


class TestQuality:
    @pytest.mark.asyncio
    async def test_profile(self, engine: DataEngine) -> None:
        from SuperDev.data.data_models import DataRecord

        records = [DataRecord(source="s", data={"id": i, "value": i * 2}) for i in range(10)]
        report = engine.quality.profile(records, "asset-1")
        assert report.completeness == 1.0
        assert report.uniqueness == 1.0


class TestCatalog:
    @pytest.mark.asyncio
    async def test_search_and_lineage(self, engine: DataEngine) -> None:
        asset = engine.catalog.register_asset("sales_table", "table", owner="analytics")
        parent = engine.catalog.register_asset("sales_raw", "lake_object")
        assert engine.catalog.add_lineage(asset.asset_id, parent.asset_id)
        assert engine.catalog.lineage_of(asset.asset_id) == [parent.asset_id]
        results = engine.catalog.search("sales")
        assert len(results) >= 1


class TestDeepDiveToolkits:
    """Wiring of the deep-dive modules into the subsystem engines."""

    @pytest.mark.asyncio
    async def test_forecasting_time_series(self, engine: DataEngine) -> None:
        analyzer = engine.forecasting.time_series
        report = analyzer.analyze([1.0, 2.0, 3.0], period=2)
        assert report["length"] == 3
        assert report["mean"] == 2.0
        assert engine.metrics.get_counter("forecasting.analyses") >= 1
        assert analyzer.history()

    @pytest.mark.asyncio
    async def test_quality_profiler(self, engine: DataEngine) -> None:
        from SuperDev.data.data_models import DataRecord

        records = [DataRecord(source="s", data={"v": i}) for i in range(3)]
        report = engine.quality.profiler.profile(records, asset_id="wired")
        assert report["records"] == 3
        assert engine.metrics.get_counter("quality.profiling_runs", {"asset": "wired"}) >= 1

    @pytest.mark.asyncio
    async def test_streaming_streams(self, engine: DataEngine) -> None:
        stream = engine.streaming.streams.create("wired")
        await engine.streaming.streams.publish("wired", {"v": 1})
        assert stream.size() == 1
        assert engine.metrics.get_counter("streaming.published", {"stream": "wired"}) >= 1


class TestStreaming:
    @pytest.mark.asyncio
    async def test_publish_and_aggregate(self, engine: DataEngine) -> None:
        for i in range(5):
            await engine.streaming.publish("sensor", {"value": i})
        agg = engine.streaming.aggregate("sensor", "value")
        assert agg["count"] == 5
        assert agg["sum"] == 10

    @pytest.mark.asyncio
    async def test_window(self, engine: DataEngine) -> None:
        for i in range(5):
            await engine.streaming.publish("w", {"v": i})
        windows = engine.streaming.window("w", size=2)
        assert all(len(w) <= 2 for w in windows)
