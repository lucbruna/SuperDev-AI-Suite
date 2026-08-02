"""Comprehensive tests for business_intelligence subsystem (Volume 33)."""

import os
import sys
import unittest

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.business_intelligence.bi_config import BIConfig, ConfigEntry
from ai.business_intelligence.bi_context import BIContext, BIContextItem
from ai.business_intelligence.bi_engine import BIEngine
from ai.business_intelligence.bi_events import BIEvent, BIEventBus, BIEventType
from ai.business_intelligence.bi_factory import BIFactory
from ai.business_intelligence.bi_logger import BILogEntry, BILogger, BILogLevel
from ai.business_intelligence.bi_manager import BIManager, BIProject
from ai.business_intelligence.bi_metrics import BIMetrics, MetricPoint, MetricSummary
from ai.business_intelligence.bi_models import (
    KPI,
    AnalysisType,
    DataPoint,
    DataSource,
    DataSourceType,
    Decision,
    DecisionType,
    Insight,
    MetricType,
    Prediction,
    Report,
    RiskLevel,
)
from ai.business_intelligence.bi_protocols import BIProtocolConfig, BIProtocols, BIProtocolType
from ai.business_intelligence.bi_registry import BIComponent, BIRegistry
from ai.business_intelligence.bi_runtime import BIRuntime, BITask, BITaskState
from ai.business_intelligence.bi_security import BISecurity, BISecurityCheck, BISecurityIssue, BISeverity


class TestBIModels(unittest.TestCase):
    def test_data_source_type(self):
        self.assertEqual(DataSourceType.DATABASE.value, "database")
        self.assertEqual(DataSourceType.API.value, "api")
        self.assertEqual(DataSourceType.FILE.value, "file")
        self.assertEqual(DataSourceType.STREAM.value, "stream")

    def test_analysis_type(self):
        self.assertEqual(AnalysisType.DESCRIPTIVE.value, "descriptive")
        self.assertEqual(AnalysisType.PREDICTIVE.value, "predictive")
        self.assertEqual(AnalysisType.PRESCRIPTIVE.value, "prescriptive")

    def test_metric_type(self):
        self.assertEqual(MetricType.COUNTER.value, "counter")
        self.assertEqual(MetricType.GAUGE.value, "gauge")
        self.assertEqual(MetricType.CURRENCY.value, "currency")

    def test_decision_type(self):
        self.assertEqual(DecisionType.STRATEGIC.value, "strategic")
        self.assertEqual(DecisionType.TACTICAL.value, "tactical")
        self.assertEqual(DecisionType.FINANCIAL.value, "financial")

    def test_risk_level(self):
        self.assertEqual(RiskLevel.LOW.value, "low")
        self.assertEqual(RiskLevel.CRITICAL.value, "critical")

    def test_data_source(self):
        ds = DataSource(source_id="s1", name="Test", source_type=DataSourceType.DATABASE)
        self.assertEqual(ds.source_id, "s1")
        self.assertEqual(ds.source_type, DataSourceType.DATABASE)
        self.assertTrue(ds.active)

    def test_data_point(self):
        dp = DataPoint(point_id="p1", value=42.0)
        self.assertEqual(dp.value, 42.0)

    def test_kpi(self):
        kpi = KPI(kpi_id="k1", name="Revenue", target=100000, current=75000)
        self.assertEqual(kpi.current, 75000)
        self.assertAlmostEqual(kpi.achievement, 75.0)

    def test_kpi_status_on_track(self):
        kpi = KPI(kpi_id="k1", name="Test", target=100, current=110)
        self.assertEqual(kpi.status, "on_track")

    def test_kpi_status_warning(self):
        kpi = KPI(kpi_id="k1", name="Test", target=100, current=80, threshold_warning=70)
        self.assertEqual(kpi.status, "warning")

    def test_kpi_status_critical(self):
        kpi = KPI(kpi_id="k1", name="Test", target=100, current=50, threshold_warning=70)
        self.assertEqual(kpi.status, "critical")

    def test_insight(self):
        ins = Insight(insight_id="i1", title="Test", description="desc", confidence=0.9)
        self.assertEqual(ins.confidence, 0.9)
        self.assertEqual(ins.impact, "medium")

    def test_prediction(self):
        pred = Prediction(
            prediction_id="p1", target_metric="revenue", predicted_value=50000, confidence_interval=(45000, 55000)
        )
        self.assertEqual(pred.predicted_value, 50000)

    def test_decision(self):
        dec = Decision(decision_id="d1", decision_type=DecisionType.STRATEGIC, recommendation="approve")
        self.assertEqual(dec.recommendation, "approve")
        self.assertEqual(dec.status, "pending")

    def test_report(self):
        rep = Report(report_id="r1", title="Monthly", report_type="financial")
        self.assertEqual(rep.report_type, "financial")
        self.assertEqual(rep.author, "BI Engine")


class TestBIConfig(unittest.TestCase):
    def test_config_entry(self):
        entry = ConfigEntry(key="k", value="v")
        self.assertEqual(entry.key, "k")

    def test_bi_config_set_get(self):
        config = BIConfig()
        config.set("debug", True)
        self.assertTrue(config.get("debug"))

    def test_bi_config_missing(self):
        config = BIConfig()
        self.assertIsNone(config.get("missing"))


class TestBIEngine(unittest.TestCase):
    def test_engine_init(self):
        engine = BIEngine()
        self.assertIsNotNone(engine)

    def test_engine_register_source(self):
        engine = BIEngine()
        ds = DataSource(source_id="s1", name="Test")
        sid = engine.register_source(ds)
        self.assertEqual(sid, "s1")

    def test_engine_ingest_data(self):
        engine = BIEngine()
        points = [DataPoint(point_id="p1", value=10.0), DataPoint(point_id="p2", value=20.0)]
        count = engine.ingest_data(points)
        self.assertEqual(count, 2)

    def test_engine_add_kpi(self):
        engine = BIEngine()
        kpi = KPI(kpi_id="k1", name="Revenue", target=100)
        kid = engine.add_kpi(kpi)
        self.assertEqual(kid, "k1")
        found = engine.get_kpi("k1")
        self.assertIsNotNone(found)

    def test_engine_add_insight(self):
        engine = BIEngine()
        ins = Insight(insight_id="i1", title="Trend")
        iid = engine.add_insight(ins)
        self.assertEqual(iid, "i1")
        self.assertEqual(len(engine.get_insights()), 1)

    def test_engine_add_prediction(self):
        engine = BIEngine()
        pred = Prediction(prediction_id="p1", target_metric="revenue", predicted_value=50000)
        engine.add_prediction(pred)
        self.assertEqual(len(engine.get_predictions()), 1)

    def test_engine_add_decision(self):
        engine = BIEngine()
        dec = Decision(decision_id="d1", recommendation="go")
        engine.add_decision(dec)
        self.assertEqual(len(engine.get_decisions()), 1)

    def test_engine_stats(self):
        engine = BIEngine()
        engine.register_source(DataSource(source_id="s1", name="A"))
        engine.ingest_data([DataPoint(point_id="p1", value=1.0)])
        engine.add_kpi(KPI(kpi_id="k1", name="K"))
        stats = engine.get_stats()
        self.assertEqual(stats["sources"], 1)
        self.assertEqual(stats["data_points"], 1)
        self.assertEqual(stats["kpis"], 1)


class TestBIManager(unittest.TestCase):
    def test_project(self):
        proj = BIProject(project_id="p1", name="Test")
        self.assertEqual(proj.name, "Test")
        self.assertEqual(proj.status, "active")

    def test_manager_create_project(self):
        mgr = BIManager()
        proj = mgr.create_project("Test Project")
        self.assertIsNotNone(proj.project_id)
        self.assertEqual(proj.name, "Test Project")

    def test_manager_list_projects(self):
        mgr = BIManager()
        mgr.create_project("A")
        mgr.create_project("B")
        self.assertEqual(len(mgr.list_projects()), 2)

    def test_manager_get_project(self):
        mgr = BIManager()
        proj = mgr.create_project("Test")
        found = mgr.get_project(proj.project_id)
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Test")

    def test_manager_artifacts(self):
        mgr = BIManager()
        proj = mgr.create_project("Test")
        artifact = mgr.add_artifact(proj.project_id, "report", {"title": "Q1"})
        self.assertEqual(artifact["type"], "report")
        artifacts = mgr.get_artifacts(proj.project_id)
        self.assertEqual(len(artifacts), 1)

    def test_manager_approve(self):
        mgr = BIManager()
        proj = mgr.create_project("Test")
        result = mgr.approve(proj.project_id, "admin")
        self.assertTrue(result)


class TestBIFactory(unittest.TestCase):
    def test_factory_init(self):
        factory = BIFactory()
        self.assertIsNotNone(factory)

    def test_factory_create_kpi(self):
        factory = BIFactory()
        kpi = factory.create_kpi("Revenue", target=100000, metric_type=MetricType.CURRENCY)
        self.assertEqual(kpi.name, "Revenue")
        self.assertEqual(kpi.target, 100000)

    def test_factory_create_kpi_from_template(self):
        factory = BIFactory()
        kpi = factory.create_kpi_from_template("revenue_kpi")
        self.assertEqual(kpi.name, "Revenue")

    def test_factory_create_insight(self):
        factory = BIFactory()
        ins = factory.create_insight("Trend", "Revenue is up")
        self.assertEqual(ins.title, "Trend")

    def test_factory_create_prediction(self):
        factory = BIFactory()
        pred = factory.create_prediction("revenue", 50000, horizon="30d")
        self.assertEqual(pred.predicted_value, 50000)

    def test_factory_create_decision(self):
        factory = BIFactory()
        dec = factory.create_decision("Expand?", [{"name": "yes"}, {"name": "no"}])
        self.assertEqual(dec.title, "Expand?")

    def test_factory_create_source(self):
        factory = BIFactory()
        src = factory.create_source("DB", source_type="database")
        self.assertEqual(src.name, "DB")

    def test_factory_templates(self):
        factory = BIFactory()
        templates = factory.list_templates()
        self.assertIn("revenue_kpi", templates)


class TestBIRegistry(unittest.TestCase):
    def test_component(self):
        comp = BIComponent(component_id="c1", name="TestComp")
        self.assertEqual(comp.name, "TestComp")
        self.assertEqual(comp.version, "1.0")

    def test_registry_register(self):
        reg = BIRegistry()
        comp = reg.register("c1", "TestComp", component_type="engine")
        self.assertEqual(comp.component_id, "c1")

    def test_registry_get(self):
        reg = BIRegistry()
        reg.register("c1", "A")
        found = reg.get("c1")
        self.assertIsNotNone(found)

    def test_registry_get_by_type(self):
        reg = BIRegistry()
        reg.register("c1", "A", component_type="engine")
        reg.register("c2", "B", component_type="dashboard")
        engines = reg.get_by_type("engine")
        self.assertEqual(len(engines), 1)

    def test_registry_deregister(self):
        reg = BIRegistry()
        reg.register("c1", "A")
        result = reg.deregister("c1")
        self.assertTrue(result)
        self.assertIsNone(reg.get("c1"))

    def test_registry_dependencies(self):
        reg = BIRegistry()
        reg.register("c1", "A")
        reg.register("c2", "B")
        reg.add_dependency("c1", "c2")
        deps = reg.get_dependencies("c1")
        self.assertEqual(deps, ["c2"])

    def test_registry_count(self):
        reg = BIRegistry()
        reg.register("c1", "A")
        reg.register("c2", "B")
        self.assertEqual(reg.count(), 2)


class TestBIRuntime(unittest.TestCase):
    def test_task_state(self):
        self.assertEqual(BITaskState.PENDING.value, "pending")
        self.assertEqual(BITaskState.RUNNING.value, "running")
        self.assertEqual(BITaskState.COMPLETED.value, "completed")
        self.assertEqual(BITaskState.FAILED.value, "failed")
        self.assertEqual(BITaskState.CANCELLED.value, "cancelled")

    def test_task(self):
        task = BITask(task_id="t1", project_id="p1", name="TestTask")
        self.assertEqual(task.state, BITaskState.PENDING)

    def test_runtime_submit_task(self):
        runtime = BIRuntime()
        task = runtime.submit_task("p1", "TestTask")
        self.assertIsNotNone(task.task_id)
        self.assertEqual(runtime.count(), 1)

    def test_runtime_execute_task(self):
        runtime = BIRuntime()
        task = runtime.submit_task("p1", "TestTask")
        result = runtime.execute_task(task.task_id)
        self.assertTrue(result)

    def test_runtime_execute_with_handler(self):
        runtime = BIRuntime()
        runtime.register_handler("custom", lambda x: {"result": "done"})
        task = runtime.submit_task("p1", "custom")
        result = runtime.execute_task(task.task_id)
        self.assertTrue(result)
        self.assertEqual(task.output_data["result"], "done")

    def test_runtime_cancel_task(self):
        runtime = BIRuntime()
        task = runtime.submit_task("p1", "TestTask")
        result = runtime.cancel_task(task.task_id)
        self.assertTrue(result)
        self.assertEqual(task.state, BITaskState.CANCELLED)

    def test_runtime_get_task(self):
        runtime = BIRuntime()
        task = runtime.submit_task("p1", "TestTask")
        found = runtime.get_task(task.task_id)
        self.assertIsNotNone(found)


class TestBIContext(unittest.TestCase):
    def test_context_item(self):
        item = BIContextItem(key="k", value="v")
        self.assertEqual(item.key, "k")
        self.assertEqual(item.scope, "global")

    def test_context_set_get(self):
        ctx = BIContext()
        ctx.set("key1", "val1")
        self.assertEqual(ctx.get("key1"), "val1")

    def test_context_missing(self):
        ctx = BIContext()
        self.assertIsNone(ctx.get("missing"))

    def test_context_delete(self):
        ctx = BIContext()
        ctx.set("key1", "val1")
        result = ctx.delete("key1")
        self.assertTrue(result)
        self.assertIsNone(ctx.get("key1"))

    def test_context_get_all(self):
        ctx = BIContext()
        ctx.set("a", 1)
        ctx.set("b", 2)
        all_items = ctx.get_all()
        self.assertEqual(len(all_items), 2)

    def test_context_count(self):
        ctx = BIContext()
        ctx.set("a", 1)
        ctx.set("b", 2)
        self.assertEqual(ctx.count(), 2)

    def test_context_project_scoped(self):
        ctx = BIContext()
        ctx.set("key", "global_val")
        ctx.set("other_key", "proj_val", project_id="p1")
        self.assertEqual(ctx.get("key"), "global_val")
        self.assertEqual(ctx.get("other_key", project_id="p1"), "proj_val")


class TestBIEvents(unittest.TestCase):
    def test_event_type(self):
        self.assertEqual(BIEventType.DATA_INGESTED.value, "data_ingested")
        self.assertEqual(BIEventType.KPI_UPDATED.value, "kpi_updated")
        self.assertEqual(BIEventType.ANOMALY_DETECTED.value, "anomaly_detected")

    def test_event(self):
        evt = BIEvent(event_id="e1", event_type=BIEventType.DATA_INGESTED, source="test")
        self.assertEqual(evt.event_type, BIEventType.DATA_INGESTED)
        self.assertEqual(evt.source, "test")

    def test_event_bus_publish(self):
        bus = BIEventBus()
        evt = bus.publish(BIEventType.DATA_INGESTED, "test_source", {"rows": 100})
        self.assertIsNotNone(evt.event_id)
        self.assertEqual(bus.count(), 1)

    def test_event_bus_subscribe(self):
        bus = BIEventBus()
        received = []
        bus.subscribe(BIEventType.DATA_INGESTED, lambda e: received.append(e))
        bus.publish(BIEventType.DATA_INGESTED, "src")
        self.assertEqual(len(received), 1)

    def test_event_bus_get_events(self):
        bus = BIEventBus()
        bus.publish(BIEventType.DATA_INGESTED, "src1")
        bus.publish(BIEventType.KPI_UPDATED, "src2")
        events = bus.get_events(event_type=BIEventType.DATA_INGESTED)
        self.assertEqual(len(events), 1)


class TestBIMetrics(unittest.TestCase):
    def test_metric_point(self):
        mp = MetricPoint(name="cpu", value=75.5)
        self.assertEqual(mp.value, 75.5)

    def test_metric_summary(self):
        ms = MetricSummary(name="cpu", count=10, avg_val=50.0, min_val=10.0, max_val=90.0)
        self.assertEqual(ms.count, 10)

    def test_bi_metrics_record(self):
        metrics = BIMetrics()
        mp = metrics.record("cpu", 80.0)
        self.assertEqual(mp.value, 80.0)

    def test_bi_metrics_record_multiple(self):
        metrics = BIMetrics()
        metrics.record("cpu", 80.0)
        metrics.record("cpu", 90.0)
        summary = metrics.get_summary("cpu")
        self.assertEqual(summary.count, 2)
        self.assertAlmostEqual(summary.avg_val, 85.0)

    def test_bi_metrics_get_all(self):
        metrics = BIMetrics()
        metrics.record("cpu", 80.0)
        metrics.record("mem", 50.0)
        all_metrics = metrics.get_all_metrics()
        self.assertEqual(len(all_metrics), 2)


class TestBILogger(unittest.TestCase):
    def test_log_level(self):
        self.assertEqual(BILogLevel.INFO.value, "info")
        self.assertEqual(BILogLevel.ERROR.value, "error")

    def test_log_entry(self):
        entry = BILogEntry(level=BILogLevel.INFO, message="test msg")
        self.assertEqual(entry.message, "test msg")

    def test_logger_info(self):
        logger = BILogger()
        entry = logger.info("test info")
        self.assertEqual(entry.message, "test info")

    def test_logger_error(self):
        logger = BILogger()
        entry = logger.error("test error")
        self.assertEqual(entry.level, BILogLevel.ERROR)

    def test_logger_get_entries(self):
        logger = BILogger()
        logger.info("info msg")
        logger.error("error msg")
        entries = logger.get_entries()
        self.assertEqual(len(entries), 2)

    def test_logger_filter_level(self):
        logger = BILogger()
        logger.info("info msg")
        logger.error("error msg")
        errors = logger.get_entries(level=BILogLevel.ERROR)
        self.assertEqual(len(errors), 1)

    def test_logger_count(self):
        logger = BILogger()
        logger.info("a")
        logger.info("b")
        self.assertEqual(logger.count(), 2)


class TestBIProtocols(unittest.TestCase):
    def test_protocol_type(self):
        self.assertEqual(BIProtocolType.REST.value, "rest")
        self.assertEqual(BIProtocolType.GRPC.value, "grpc")

    def test_protocol_config(self):
        config = BIProtocolConfig(name="api_v1", protocol_type=BIProtocolType.REST, base_url="/api/v1")
        self.assertEqual(config.base_url, "/api/v1")

    def test_protocols_register(self):
        protos = BIProtocols()
        config = protos.register("api_v1", BIProtocolType.REST, base_url="/api")
        self.assertEqual(config.name, "api_v1")

    def test_protocols_get(self):
        protos = BIProtocols()
        protos.register("api_v1", BIProtocolType.REST)
        found = protos.get("api_v1")
        self.assertIsNotNone(found)

    def test_protocols_list(self):
        protos = BIProtocols()
        protos.register("a", BIProtocolType.REST)
        protos.register("b", BIProtocolType.GRPC)
        self.assertEqual(len(protos.list_protocols()), 2)

    def test_protocols_count(self):
        protos = BIProtocols()
        protos.register("a", BIProtocolType.REST)
        self.assertEqual(protos.count(), 1)


class TestBISecurity(unittest.TestCase):
    def test_security_check(self):
        self.assertEqual(BISecurityCheck.DATA_ACCESS.value, "data_access")
        self.assertEqual(BISecurityCheck.PERMISSION.value, "permission")
        self.assertEqual(BISecurityCheck.ENCRYPTION.value, "encryption")

    def test_severity(self):
        self.assertEqual(BISeverity.LOW.value, "low")
        self.assertEqual(BISeverity.CRITICAL.value, "critical")

    def test_security_issue(self):
        issue = BISecurityIssue(
            issue_id="i1", check=BISecurityCheck.PERMISSION, severity=BISeverity.HIGH, description="test"
        )
        self.assertEqual(issue.severity, BISeverity.HIGH)
        self.assertFalse(issue.resolved)

    def test_security_report_issue(self):
        sec = BISecurity()
        issue = sec.report_issue(BISecurityCheck.PERMISSION, BISeverity.LOW, description="ok")
        self.assertIsNotNone(issue.issue_id)

    def test_security_get_issues(self):
        sec = BISecurity()
        sec.report_issue(BISecurityCheck.PERMISSION, BISeverity.LOW, description="a")
        sec.report_issue(BISecurityCheck.ENCRYPTION, BISeverity.HIGH, description="b")
        issues = sec.get_issues()
        self.assertEqual(len(issues), 2)

    def test_security_filter_severity(self):
        sec = BISecurity()
        sec.report_issue(BISecurityCheck.PERMISSION, BISeverity.LOW, description="a")
        sec.report_issue(BISecurityCheck.ENCRYPTION, BISeverity.HIGH, description="b")
        high_issues = sec.get_issues(severity=BISeverity.HIGH)
        self.assertEqual(len(high_issues), 1)

    def test_security_resolve(self):
        sec = BISecurity()
        issue = sec.report_issue(BISecurityCheck.AUDIT, BISeverity.MEDIUM, description="test")
        result = sec.resolve_issue(issue.issue_id)
        self.assertTrue(result)
        self.assertTrue(issue.resolved)

    def test_security_score(self):
        sec = BISecurity()
        self.assertEqual(sec.get_score(), 100.0)
        sec.report_issue(BISecurityCheck.AUDIT, BISeverity.LOW, description="a")
        self.assertEqual(sec.get_score(), 95.0)

    def test_security_policies(self):
        sec = BISecurity()
        sec.create_policy("data_policy", {"max_access": 100})
        self.assertIn("data_policy", sec.policies)


if __name__ == "__main__":
    unittest.main()
