from __future__ import annotations

import pytest

from SuperDev.monitoring.monitoring_models import (
    MetricType,
    LogLevel,
    SpanStatus,
    AlertSeverity,
    AlertStatus,
    DashboardVisibility,
    HealthStatus,
    AnomalySeverity,
    RecoveryAction,
    MetricSample,
    MetricMetadata,
    LogEntry,
    Alert,
)


class TestEnums:
    def test_metric_type_values(self) -> None:
        assert MetricType.COUNTER.value == "counter"
        assert MetricType.GAUGE.value == "gauge"
        assert MetricType.HISTOGRAM.value == "histogram"

    def test_log_level_values(self) -> None:
        assert LogLevel.INFO.value == "INFO"
        assert LogLevel.ERROR.value == "ERROR"

    def test_span_status_values(self) -> None:
        assert SpanStatus.OK.value == "ok"
        assert SpanStatus.ERROR.value == "error"

    def test_alert_severity_order(self) -> None:
        assert AlertSeverity.CRITICAL > AlertSeverity.WARNING

    def test_health_status_values(self) -> None:
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"


class TestDataclasses:
    def test_metric_sample_defaults(self) -> None:
        s = MetricSample(
            name="test", value=1.0, metric_type=MetricType.GAUGE
        )
        assert s.labels == {}
        assert s.timestamp > 0

    def test_log_entry(self) -> None:
        e = LogEntry(
            message="test",
            level=LogLevel.INFO,
            logger="test",
        )
        assert e.message == "test"

    def test_alert_defaults(self) -> None:
        a = Alert(
            id="a1",
            name="alert1",
            severity=AlertSeverity.WARNING,
            message="test",
        )
        assert a.status == AlertStatus.FIRING

    def test_recovery_action_defaults(self) -> None:
        a = RecoveryAction(
            action_type="restart",
            target="svc",
            reason="fail",
        )
        assert a.status == "pending"
