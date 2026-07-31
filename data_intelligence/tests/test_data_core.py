"""Smoke tests for the Data Intelligence core (Volume 22, Fase 1)."""

from __future__ import annotations

from data_intelligence.data_config import DataIntelligenceConfig
from data_intelligence.data_context import DataIntelligenceContext
from data_intelligence.data_engine import DataIntelligenceEngine
from data_intelligence.data_events import (DataIntelligenceEventType,
                                           DataIntelligenceEvents)
from data_intelligence.data_factory import build_engine
from data_intelligence.data_manager import DataIntelligenceManager
from data_intelligence.data_metrics import DataIntelligenceMetrics
from data_intelligence.data_models import (AnalyticsLevel, AnalyticsResult,
                                           DataClassification, DataRecord,
                                           DataSource, ModelRecord,
                                           ModelStatus, PipelineStatus,
                                           ReportFormat, SourceType)
from data_intelligence.data_protocols import (coerce_bool, coerce_number,
                                              new_id, numeric_values,
                                              safe_get)
from data_intelligence.data_registry import DataIntelligenceRegistry
from data_intelligence.data_runtime import DataIntelligenceRuntime
from data_intelligence.data_security import DataIntelligenceSecurity


class TestConfig:
    def test_merge(self) -> None:
        config = DataIntelligenceConfig()
        merged = config.merge(max_batch_size=500, locale="en")
        assert config.max_batch_size == 1000  # original untouched
        assert merged.max_batch_size == 500
        assert merged.locale == "en"


class TestModels:
    def test_source_enum(self) -> None:
        assert SourceType.SQL.value == "sql"
        assert SourceType.IOT.value == "iot"

    def test_analytics_result(self) -> None:
        result = AnalyticsResult(AnalyticsLevel.DESCRIPTIVE, "receita",
                                 value=1000)
        assert result.to_dict()["value"] == 1000
        assert result.to_dict()["level"] == "descriptive"

    def test_classification(self) -> None:
        assert DataClassification.CONFIDENTIAL.value == "confidential"


class TestEvents:
    def test_on_publish_off(self) -> None:
        events = DataIntelligenceEvents()
        seen: list[str] = []
        listener = lambda e: seen.append(e["type"])  # noqa: E731
        events.on(DataIntelligenceEventType.INGESTION_COMPLETED, listener)
        events.publish(DataIntelligenceEventType.INGESTION_COMPLETED,
                       {"source_id": "s1"})
        assert seen == ["ingestion.completed"]
        events.off(DataIntelligenceEventType.INGESTION_COMPLETED, listener)
        events.publish(DataIntelligenceEventType.INGESTION_COMPLETED)
        assert len(seen) == 1
        assert events.listener_count(
            DataIntelligenceEventType.INGESTION_COMPLETED) == 0

    def test_once(self) -> None:
        events = DataIntelligenceEvents()
        calls = []
        events.once(DataIntelligenceEventType.MODEL_TRAINED,
                    lambda e: calls.append(1))
        events.publish(DataIntelligenceEventType.MODEL_TRAINED)
        events.publish(DataIntelligenceEventType.MODEL_TRAINED)
        assert len(calls) == 1


class TestMetrics:
    def test_snapshot(self) -> None:
        metrics = DataIntelligenceMetrics()
        metrics.increment("ingestions.completed")
        metrics.increment("ingestions.completed")
        metrics.gauge("storage.bytes", 42.0)
        with metrics.timed("pipeline.run"):
            pass
        snapshot = metrics.snapshot()
        assert snapshot["counters"]["ingestions.completed"] == 2
        assert snapshot["gauges"]["storage.bytes"] == 42.0
        assert snapshot["timings"]["pipeline.run"][1] == 1


class TestSecurity:
    def test_mask_pii(self) -> None:
        security = DataIntelligenceSecurity()
        assert security.mask_pii("joao@gmail.com") == "j***@gmail.com"
        assert security.mask_pii("12345678901", "cpf") == "123.***.***-01"
        assert security.mask_pii("JOAO SILVA", "name") == "JOAO S."
        assert security.mask_pii(None) is None

    def test_classify_and_permissions(self) -> None:
        security = DataIntelligenceSecurity()
        assert security.classify("customer_pii") is DataClassification.CONFIDENTIAL
        assert security.classify("sales") is DataClassification.INTERNAL
        assert security.classify("public_pages") is DataClassification.PUBLIC
        security.grant("analyst", "sales")
        assert security.can_access("analyst", "sales") is True
        assert security.can_access("analyst", "finance") is False

    def test_audit(self) -> None:
        security = DataIntelligenceSecurity()
        security.audit("analyst", "read", "sales")
        assert len(security.audit_log()) == 1


class TestProtocols:
    def test_safe_get(self) -> None:
        data = {"a": {"b": {"c": 1}}}
        assert safe_get(data, "a.b.c") == 1
        assert safe_get(data, "a.x", default=0) == 0

    def test_numeric_values(self) -> None:
        records = [{"v": "10"}, {"v": 5}, {"v": "n/a"}]
        assert numeric_values(records, "v") == [10.0, 5.0]

    def test_coerce(self) -> None:
        assert coerce_bool("sim") is True
        assert coerce_number("1.5") == 1.5
        assert new_id("src").startswith("src-")


class TestRegistry:
    def test_crud(self) -> None:
        registry = DataIntelligenceRegistry()
        registry.register_source("s1", object())
        registry.register_model("m1", object())
        registry.register_dashboard("d1", object())
        registry.register_report("r1", object())
        assert registry.list_sources() == ["s1"]
        assert registry.get_model("m1") is not None
        assert registry.list_dashboards() == ["d1"]
        assert registry.list_reports() == ["r1"]
        assert registry.stats() == {"sources": 1, "models": 1,
                                    "dashboards": 1, "reports": 1}
        assert registry.remove_source("s1") is True
        assert registry.remove_source("s1") is False
        assert registry.remove_model("m1") is True
        assert registry.remove_dashboard("d1") is True
        assert registry.remove_report("r1") is True


class TestRuntime:
    def test_start_stop_idempotent(self) -> None:
        runtime = DataIntelligenceRuntime()
        assert runtime.start() is True
        assert runtime.start() is False
        assert runtime.running is True
        assert runtime.stop() is True
        assert runtime.stop() is False
        assert runtime.state()["running"] is False


class TestContext:
    def test_set_get_clear(self) -> None:
        context = DataIntelligenceContext()
        context.set("user", "ana")
        assert context.get("user") == "ana"
        assert context.attributes() == {"user": "ana"}
        context.clear()
        assert context.get("user") is None


class TestManagerAndEngine:
    def test_register_and_ingest(self) -> None:
        engine = build_engine()
        engine.register_source("s-erp", "ERP NEXUS", SourceType.ERP)
        assert engine.list_sources() == ["s-erp"]
        result = engine.ingest("s-erp", [{"venda": 100}, {"venda": 200}])
        assert result["ingested"] == 2

    def test_ingest_unknown_source(self) -> None:
        engine = build_engine()
        try:
            engine.ingest("ghost", [])
            raised = False
        except ValueError:
            raised = True
        assert raised is True

    def test_attach_subsystem(self) -> None:
        engine = build_engine()

        class FakeAnalytics:
            def compute(self, metric: str, data: list[dict[str, object]]) -> dict[str, object]:
                return {"metric": metric, "value": len(data)}

        engine.attach_subsystem("analytics", FakeAnalytics())
        assert engine.analytics.compute("receita", [{"a": 1}])["value"] == 1
        assert engine.manager.analytics_engine is engine.analytics
        assert engine.analyze("receita", [{"a": 1}, {"a": 2}])["value"] == 2

    def test_factory_overrides(self) -> None:
        engine = build_engine(max_batch_size=777)
        assert engine.config.max_batch_size == 777
        assert isinstance(engine.manager, DataIntelligenceManager)
        assert isinstance(engine.metrics, DataIntelligenceMetrics)

    def test_lifecycle_and_stats(self) -> None:
        engine = build_engine()
        assert engine.start() is True
        assert engine.run() is False  # already running
        stats = engine.stats()
        assert "registry" in stats and "runtime" in stats
        assert engine.stop() is True

    def test_manager_engine_backref(self) -> None:
        engine = build_engine()
        assert engine.manager.engine is engine
