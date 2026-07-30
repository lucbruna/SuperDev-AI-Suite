from __future__ import annotations

from ..alert_manager import AlertManager
from ..anomaly_detector import AnomalyDetector
from ..dashboard_generator import DashboardGenerator
from ..health_checks import HealthChecks
from ..log_analysis import LogAnalysis
from ..metrics_collector import MetricsCollector
from ..monitoring_agent import MonitoringEngine
from ..sla_monitor import SLAMonitor
from ..tracing import Tracing


class TestMetricsCollector:
    def test_collect(self) -> None:
        mc = MetricsCollector()
        mc.collect("cpu", 50.0)
        assert mc.metric_count == 1

    def test_get_metric(self) -> None:
        mc = MetricsCollector()
        mc.collect("cpu", 50.0)
        assert mc.get_metric("cpu") == [50.0]

    def test_list_metrics(self) -> None:
        mc = MetricsCollector()
        mc.collect("a", 1)
        assert "a" in mc.list_metrics()

    def test_summary(self) -> None:
        mc = MetricsCollector()
        mc.collect("latency", 10)
        mc.collect("latency", 20)
        s = mc.summary("latency")
        assert s["avg"] == 15.0

    def test_to_dict(self) -> None:
        mc = MetricsCollector()
        mc.collect("m", 1)
        d = mc.to_dict()
        assert "metrics" in d


class TestTracing:
    def test_start_span(self) -> None:
        t = Tracing()
        t.start_span("request")
        assert t.span_count == 1

    def test_end_span(self) -> None:
        t = Tracing()
        t.start_span("request")
        assert t.end_span("request") is True

    def test_get_trace(self) -> None:
        t = Tracing()
        t.start_span("a", "trace1")
        assert t.get_trace("trace1") == ["a"]

    def test_to_dict(self) -> None:
        t = Tracing()
        t.start_span("s")
        d = t.to_dict()
        assert "spans" in d


class TestLogAnalysis:
    def test_ingest_entry(self) -> None:
        la = LogAnalysis()
        la.ingest_entry({"id": "1", "message": "hello"})
        assert la.entry_count == 1

    def test_search(self) -> None:
        la = LogAnalysis()
        la.ingest_entry({"id": "1", "message": "error occurred"})
        la.ingest_entry({"id": "2", "message": "all good"})
        results = la.search("error")
        assert len(results) == 1

    def test_get_stats(self) -> None:
        la = LogAnalysis()
        la.ingest_entry({"id": "1"})
        stats = la.get_stats()
        assert stats["total"] == 1

    def test_to_dict(self) -> None:
        la = LogAnalysis()
        la.ingest_entry({"id": "1"})
        d = la.to_dict()
        assert "entries" in d


class TestAnomalyDetector:
    def test_add_baseline(self) -> None:
        ad = AnomalyDetector()
        ad.add_baseline("cpu", 50.0, 10.0)
        assert ad.baseline_count == 1

    def test_get_baseline(self) -> None:
        ad = AnomalyDetector()
        ad.add_baseline("cpu", 50, 10)
        assert ad.get_baseline("cpu") is not None

    def test_detect_anomaly(self) -> None:
        ad = AnomalyDetector()
        ad.add_baseline("cpu", 50.0, 10.0)
        result = ad.detect("cpu", 100.0)
        assert result["anomaly"] is True

    def test_detect_normal(self) -> None:
        ad = AnomalyDetector()
        ad.add_baseline("mem", 100.0, 20.0)
        result = ad.detect("mem", 110.0)
        assert result["anomaly"] is False

    def test_to_dict(self) -> None:
        ad = AnomalyDetector()
        ad.add_baseline("c", 1, 0.1)
        d = ad.to_dict()
        assert "baselines" in d


class TestAlertManager:
    def test_add_rule(self) -> None:
        am = AlertManager()
        am.add_rule("high_cpu", "cpu > 90", "critical")
        assert am.rule_count == 1

    def test_get_rule(self) -> None:
        am = AlertManager()
        am.add_rule("high_cpu", "cpu > 90")
        assert am.get_rule("high_cpu") is not None

    def test_check_rules(self) -> None:
        am = AlertManager()
        am.add_rule("high_cpu", "cpu > 90")
        results = am.check_rules({"cpu": 95.0})
        assert len(results) >= 1

    def test_to_dict(self) -> None:
        am = AlertManager()
        am.add_rule("r", "x > 1")
        d = am.to_dict()
        assert "rules" in d


class TestDashboardGenerator:
    def test_add_panel(self) -> None:
        dg = DashboardGenerator()
        dg.add_panel("CPU", "cpu_usage")
        assert dg.panel_count == 1

    def test_get_panel(self) -> None:
        dg = DashboardGenerator()
        dg.add_panel("CPU", "cpu")
        assert dg.get_panel("CPU") is not None

    def test_remove_panel(self) -> None:
        dg = DashboardGenerator()
        dg.add_panel("CPU", "cpu")
        assert dg.remove_panel("CPU") is True

    def test_generate(self) -> None:
        dg = DashboardGenerator()
        dg.add_panel("CPU", "cpu")
        result = dg.generate()
        assert "CPU" in result

    def test_to_dict(self) -> None:
        dg = DashboardGenerator()
        dg.add_panel("P", "m")
        d = dg.to_dict()
        assert "panels" in d


class TestSLAMonitor:
    def test_add_slo(self) -> None:
        sm = SLAMonitor()
        sm.add_slo("uptime", 99.9, "30d")
        assert sm.slo_count == 1

    def test_get_slo(self) -> None:
        sm = SLAMonitor()
        sm.add_slo("uptime", 99.9, "30d")
        assert sm.get_slo("uptime") is not None

    def test_record_violation(self) -> None:
        sm = SLAMonitor()
        sm.add_slo("uptime", 99.9, "30d")
        sm.record_violation("uptime")
        assert sm.to_dict()["slos"][0]["violations"] == 1

    def test_check_slos(self) -> None:
        sm = SLAMonitor()
        sm.add_slo("uptime", 99.9, "30d")
        results = sm.check_slos()
        assert len(results) == 1

    def test_to_dict(self) -> None:
        sm = SLAMonitor()
        sm.add_slo("s", 99.0, "d")
        d = sm.to_dict()
        assert "slos" in d


class TestHealthChecks:
    def test_add_check(self) -> None:
        hc = HealthChecks()
        hc.add_check("api", "/health")
        assert hc.check_count == 1

    def test_get_check(self) -> None:
        hc = HealthChecks()
        hc.add_check("api", "/health")
        assert hc.get_check("api") is not None

    def test_remove_check(self) -> None:
        hc = HealthChecks()
        hc.add_check("api", "/health")
        assert hc.remove_check("api") is True

    def test_run_checks(self) -> None:
        hc = HealthChecks()
        hc.add_check("api", "/health")
        results = hc.run_checks()
        assert results[0]["status"] == "healthy"

    def test_to_dict(self) -> None:
        hc = HealthChecks()
        hc.add_check("c", "/h")
        d = hc.to_dict()
        assert "checks" in d


class TestMonitoringEngine:
    def test_engine_initializes(self) -> None:
        me = MonitoringEngine()
        assert me.metrics is not None
        assert me.tracing is not None
        assert me.log_analysis is not None
        assert me.anomaly is not None
        assert me.alerts is not None
        assert me.dashboard is not None
        assert me.sla is not None
        assert me.health is not None

    def test_run_monitoring(self) -> None:
        me = MonitoringEngine()
        me.health.add_check("api", "/health")
        result = me.run_monitoring({})
        assert result["status"] == "monitored"

    def test_get_status(self) -> None:
        me = MonitoringEngine()
        s = me.get_status()
        assert "metrics" in s

    def test_to_dict(self) -> None:
        me = MonitoringEngine()
        d = me.to_dict()
        assert d["agent"] == "monitoring_agent"
