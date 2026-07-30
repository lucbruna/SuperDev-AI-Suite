from __future__ import annotations

import pytest

from SuperDev.monitoring.alerts.alert_manager import AlertManager
from SuperDev.monitoring.alerts.alert_rule import AlertRule
from SuperDev.monitoring.alerts.alert_evaluator import AlertEvaluator
from SuperDev.monitoring.alerts.alert_condition import AlertCondition, ConditionFn
from SuperDev.monitoring.alerts.alert_threshold import AlertThreshold, ThresholdType
from SuperDev.monitoring.alerts.alert_notifier import LogAlertNotifier
from SuperDev.monitoring.alerts.alert_suppression import AlertSuppression
from SuperDev.monitoring.alerts.alert_deduplication import AlertDeduplication
from SuperDev.monitoring.alerts.alert_aggregator import AlertAggregator


class TestAlertManager:
    def test_create_alert(self) -> None:
        mgr = AlertManager()
        mgr.create_alert(
            alert_id="a1",
            name="test",
            severity="warning",
            message="test alert",
        )
        assert len(mgr._alerts) == 1


class TestAlertRule:
    def test_rule_evaluation(self) -> None:
        rule = AlertRule(
            name="cpu_high",
            condition="cpu > 90",
            severity="critical",
            enabled=True,
        )
        assert rule.name == "cpu_high"


class TestAlertEvaluator:
    def test_evaluate(self) -> None:
        evaluator = AlertEvaluator()
        result = evaluator.evaluate(AlertRule(
            name="test", condition="", severity="info"
        ), {"value": 50})
        assert result is not None


class TestAlertCondition:
    def test_condition_fn(self) -> None:
        fn = ConditionFn.greater_than(threshold=90)
        assert fn({"value": 95})
        assert not fn({"value": 50})


class TestAlertThreshold:
    def test_threshold(self) -> None:
        t = AlertThreshold(threshold_type=ThresholdType.ABSOLUTE, value=100)
        assert t.is_breached(150)
        assert not t.is_breached(50)


class TestAlertSuppression:
    def test_suppression(self) -> None:
        s = AlertSuppression()
        assert not s.is_suppressed("a1")
        s.suppress("a1", duration=60)
        assert s.is_suppressed("a1")


class TestAlertDeduplication:
    def test_dedup(self) -> None:
        d = AlertDeduplication()
        assert not d.is_duplicate("test alert")
        assert d.is_duplicate("test alert")


class TestAlertAggregator:
    def test_aggregate(self) -> None:
        a = AlertAggregator()
        a.add_alert("cpu", "critical")
        a.add_alert("mem", "warning")
        groups = a.get_groups()
        assert len(groups) >= 1


class TestLogNotifier:
    def test_notify(self) -> None:
        n = LogAlertNotifier()
        n.notify("test", "critical", "msg")  # should not raise
