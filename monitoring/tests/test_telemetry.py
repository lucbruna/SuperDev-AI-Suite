from __future__ import annotations

import pytest

from SuperDev.monitoring.telemetry.telemetry_manager import TelemetryManager
from SuperDev.monitoring.telemetry.telemetry_event import TelemetryEvent
from SuperDev.monitoring.telemetry.telemetry_sampler import TelemetrySampler
from SuperDev.monitoring.telemetry.telemetry_batch import TelemetryBatcher
from SuperDev.monitoring.telemetry.telemetry_exporter import TelemetryExporter
from SuperDev.monitoring.telemetry.telemetry_filter import TelemetryFilter
from SuperDev.monitoring.telemetry.telemetry_context import TelemetryContext


class TestTelemetryManager:
    def test_start_stop(self) -> None:
        mgr = TelemetryManager()
        mgr.start()
        mgr.record("test")
        mgr.stop()
        mgr.record("after_stop")  # should not raise

    def test_record_event(self) -> None:
        mgr = TelemetryManager()
        mgr.start()
        mgr.record("cpu_usage", {"percent": 50})
        mgr.flush()


class TestTelemetryEvent:
    def test_to_dict(self) -> None:
        event = TelemetryEvent(name="test", data={"key": "val"})
        d = event.to_dict()
        assert d["name"] == "test"


class TestTelemetrySampler:
    def test_rate(self) -> None:
        s = TelemetrySampler(rate=1.0)
        assert s.should_sample(None) is True
        s.rate = 0.0
        assert s.should_sample(None) is False


class TestTelemetryBatcher:
    def test_batch_flush(self) -> None:
        exporter = TelemetryExporter()
        batcher = TelemetryBatcher(exporter=exporter, batch_size=5)
        for i in range(5):
            batcher.add(TelemetryEvent(name=f"e{i}"))
        # flushes automatically at batch_size


class TestTelemetryFilter:
    def test_filter_rules(self) -> None:
        f = TelemetryFilter()
        f.add_rule(lambda e: e.name != "secret")
        assert f.should_record(TelemetryEvent(name="ok"))
        assert not f.should_record(TelemetryEvent(name="secret"))


class TestTelemetryContext:
    def test_tags(self) -> None:
        ctx = TelemetryContext()
        ctx.set_tag("env", "test")
        tags = ctx.get_context()
        assert "env" in tags
        assert "host" in tags
